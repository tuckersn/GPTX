
import re


def fixResponsePacket(pBytes: bytes) -> bytes:
    # if doesn't end in /n/r then add it
    
    sections = re.split("(\r\n|\n)(\r\n|\n)", pBytes)
    
    headers = sections[0]
    headerLines = headers.split("\n")
    heading = headerLines[0]
    
    body = sections[-1]
    print("SECTIONS:", sections)
    print("BODY:", body)
        
    
    contentLengthLine = None
    for idx, line in enumerate(headerLines):
        headerLines[idx] = line.strip()
        if line.lower().startswith("content-length:"):
            contentLengthLine = idx
            break
    if contentLengthLine is None:
        print("Content-Length not found")
    
    if contentLengthLine is None:
        headerLines.append("Content-Length: " + str(len(body) - 2))
    else:
        headerLines[contentLengthLine] = "Content-Length: " + str(len(body) - 2)

    p = "\r\n".join(headerLines) + "\r\n\r\n" + body
    
    if p[-2:] != "\r\n":
        p += "\r\n"

    return p.encode("utf-8")

def responsePacketToData(packet: bytes) -> str:
    return packet.decode("utf-8").split("\r\n\r\n")[1]