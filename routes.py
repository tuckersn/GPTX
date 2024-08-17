import textwrap
import jinja2

def packet(code: int, content_type: str, content, status: str = "OK"):
    environment = jinja2.Environment()

    with open('./templates/http_1_1_packet', 'r') as content_file:
        templateStr = content_file.read()
        
    if templateStr is None:
        return "Error: Could not read template file."

    template = environment.from_string(templateStr)
    return template.render(code=code, status=status, content_type=content_type, content=content, content_length=len(content))



def deliverApp():
    try:
        with open('./templates/index.html', 'r') as content_file:
            templateStr = content_file.read()
    except FileNotFoundError:
        return "Error: Template file not found."
    except Exception as e:
        raise e

    if not templateStr:
        return "Error: Template file is empty."

    environment = jinja2.Environment()
    template = environment.from_string(templateStr)
    rendered_template = template.render(name="World")
    # Return the packet with the correctly encoded content
    return packet(200, "text/html", rendered_template)
