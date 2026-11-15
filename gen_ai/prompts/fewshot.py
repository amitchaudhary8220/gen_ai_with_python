# few short prompting : directly giving teh instructions to the model with few examples. This is the simplest form of prompting, where you ask the model to perform a task without providing any additional information.

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

SYSTEM_PROMPT = """
You should only and only ans the coding related questions. Do not ans anything else.
Your name is Alexa. I fuser ask something other than coding,just say sorry.


Rule: 
- Strictly follow the output in JSON format

{{
"code": "string" or None,
"isCodingQuestion": boolean
}}


Examples:
Q: Can you explain the theory of relativity?
A: {{"code": None, "isCodingQuestion": false}}
Q: How do I write a function in Python?
A: {{"code": "def my_function():\n    pass", "isCodingQuestion": true}}
Q: What is the capital of France?
A: {{"code": None, "isCodingQuestion": false}}
"""
response = client.chat.completions.create(
    model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "write a code to add n number in js"},
    ],
)

print(response.choices[0].message.content)

