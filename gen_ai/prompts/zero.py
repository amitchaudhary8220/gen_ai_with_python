# Zero short prompting -> directly giving the instructions to the model without any context or examples. This is the simplest form of prompting, where you ask the model to perform a task without providing any additional information.

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

SYSTEM_PROMPT = "You are expert in coading and only and only answer coading questions., If the query is not related to coading they say sorry and say I only answer coading related questions."
response = client.chat.completions.create(
    model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "how to write hello world in python"},
    ],
)

print(response.choices[0].message.content)




