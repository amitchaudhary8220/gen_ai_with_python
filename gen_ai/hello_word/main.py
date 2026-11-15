import os

from dotenv import load_dotenv
from openai import OpenAI

# Copies the KEY=value lines from .env into os.environ (like require("dotenv").config()).
load_dotenv()

# Inception Labs speaks the same API as OpenAI, so the OpenAI SDK works:
# we just point it at Inception's URL and give it Inception's key.
client = OpenAI(
    base_url="https://api.inceptionlabs.ai/v1",
    api_key=os.getenv("INCEPTION_API_KEY"),
)

response = client.chat.completions.create(
    model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
    messages=[
        {"role": "system", "content": "You are expert in maths and only and only answer maths questions., If the query is not related to maths they say sorry and say I only answer maths related questions."},
        {"role": "user", "content": "Can you give me the equation of whole square of a +b "},
    ],
)

print(response.choices[0].message.content)
