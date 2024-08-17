from dataclasses import dataclass
import socket
import ssl
import textwrap
import traceback
import jinja2
import sys

import route_llm
import routes

def create_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return context

@dataclass
class RouteContext:
    port: int = 443

def start_https_server(host='localhost', port=443, certfile='cert.pem', keyfile='key.pem'):
    
    context = RouteContext(port=port)
    ssl_context = create_ssl_context(certfile, keyfile)
    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.bind((host, port))
    bindsocket.listen(5)
    print(f'Server listening on https://{host}:{port}')

    while True:
        print("Waiting for request...")
        newsocket, fromaddr = bindsocket.accept()
        try:
            # Peek at the first byte to check if it's an HTTPS connection
            first_byte = newsocket.recv(1, socket.MSG_PEEK)
            if first_byte != b'\x16':
                # The first byte of an SSL/TLS handshake is 0x16
                # This is likely an HTTP request
                handle_http_request(newsocket, context)
            else:
                # This is an HTTPS connection
                conn = ssl_context.wrap_socket(newsocket, server_side=True)
                handle_https_request(conn, context)
        except Exception as e:
            traceback.print_exc()
            raise e
        finally:
            newsocket.close()

def handle_http_request(conn: socket.socket, context: RouteContext):
    print("Received non-HTTPS connection.")
    http_response = textwrap.dedent(f"""\
        HTTP/1.1 301 Moved Permanently\r
        Location: https://localhosat:{context.port}/\r
        Content-Type: text/plain\r
        Content-Length: 0\r
        Connection: close\r
        \r
    """)
    conn.sendall(http_response.encode('utf-8'))

def handle_https_request(conn: socket.socket, context: RouteContext):
    print("Received HTTPS connection.")
    try:
        headersStr = b""
        while True:
            chunk = conn.recv(1)
            headersStr += chunk
            if b"\r\n\r\n" in headersStr:
                break

        headers = headersStr.decode('utf-8')
        header_lines = headers.splitlines()
        content_length = 0
        for line in header_lines:
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1].strip())
                break
            print(line)

        if content_length > 0:
            body = conn.recv(content_length).decode('utf-8')
        else:
            body = ""

        if True:  # log request
            print("===========  REQUEST  ======================")
            print(headers)

        path = header_lines[0].split(' ')[1]
        if path == '/':
            response_packet = routes.deliverApp()
        else:
            response_packet = route_llm.deliverLLMGeneratedRoute(headersStr.decode("utf-8") + body)

        # Ensure response_packet is bytes-like
        if isinstance(response_packet, str):
            response_packet = response_packet.encode('utf-8')
        elif isinstance(response_packet, memoryview):
            response_packet = response_packet.tobytes()

        print(f"===========  RESPONSE ({len(response_packet)}) ======================")
        print(response_packet)
        conn.sendall(response_packet)
    except Exception as e:
        traceback.print_exc()
        raise e

    finally:
        conn.close()

if __name__ == "__main__":
    start_https_server(certfile='./certificate.pem', keyfile='./privatekey.pem', port=8000)
