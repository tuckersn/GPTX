
from openai import OpenAI

import secrets
import networking
client = OpenAI(api_key=secrets.openai_api_key())


prompt = """
You are an HTTP server, respond in complete HTTP response packets.
Do not add additional whitespace or newlines.
You are communicating with an HTMX application, you are it's API/backend.
Take whatever the user inputs and assume how you'd implement the HTMX/HTML.
You respond to every route with the intention of the user in mind.
Every respond must include a link and an interactive HTMX elment which triggers HTMX HTTP requests if you replace the main body of the page.
"""


def deliverLLMGeneratedRoute(request: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": request
            }
        ]
    )
    return networking.fixResponsePacket(completion.choices[0].message.content)
     