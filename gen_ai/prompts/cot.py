# cot - chain of thought prompting : This is a more advanced form of prompting, where you ask the model to perform a task by providing it with a series of steps or instructions. This can help the model to better understand the task and generate more accurate responses.

import os

from dotenv import load_dotenv
from openai import OpenAI
import json

# Copies the KEY=value lines from .env into os.environ (like require("dotenv").config()).
load_dotenv()

# Inception Labs speaks the same API as OpenAI, so the OpenAI SDK works:
# we just point it at Inception's URL and give it Inception's key.
client = OpenAI(
    base_url="https://api.inceptionlabs.ai/v1",
    api_key=os.getenv("INCEPTION_API_KEY"),
)

SYSTEM_PROMPT = """
   You're an expert AI Assistant in resolving user queries using chain of thought. 
   You work on START, PLAN and OUTPUT steps.
   You need to first plan that what needs to be done. The plan can be multiple steps.
   One you think enough polan has been done, finally you can give an output.

   Rules:
   - Strictly follow the output in JSON format

   - Only run one step at a time.
   - The sequence of steps is START (where user gives an input), PLAN (That can be multiple steps), and finally OUTPUT(which is going to the displayed to the user).

   Output JSON Format:
    {"step": "START" | "PLAN" | "OUTPUT", "content": "string"}

   Example:
   START: Hey, Can you solve 2 + 3 * 5 / 10
   PLAN: {"step": "PLAN", "content": "Seems like user is interested in maths problem."},
   PLAN: {"step": "PLAN", "content": "Looking at the problem, we should it with BODMAS rule."},
   PLAN: {"step": "PLAN", "content": "Yes BODMAS seems right choice for this problem."},
    PLAN: {"step": "PLAN", "content": "So, we first solve 3 * 5 = 15, "},
        PLAN: {"step": "PLAN", "content": "Then we do 15 / 10 = 1.5, "},
        PLAN: {"step": "PLAN", "content": "Then we do 2 + 1.5 = 3.5, "},
   OUTPUT: {"step": "OUTPUT", "content": "The result of the expression 2 + 3 * 5 / 10 is 1.7."}

    OUTPUT: {"step": "OUTPUT", "content": "The result of the expression 2 + 3 * 5 / 10 is 1.7."}
"""

message_history = [{"role": "system", "content": SYSTEM_PROMPT}]


print('\n\n\n')

user_query = input("👉🏻...")
message_history.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
        response_format={"type": "json_object"},
        messages=message_history,
    )

    assistant_message = response.choices[0].message.content
    print("============", assistant_message)
    message_history.append({"role": "assistant", "content": assistant_message})
    parsed_message = json.loads(assistant_message)

    if parsed_message.get("step") == "START":
        print("🔥", parsed_message.get("content"))

    if parsed_message.get("step") == "PLAN":
        print("🧠", parsed_message.get("content"))

    if parsed_message.get("step") == "OUTPUT":
        print("✅", parsed_message.get("content"))
        break


print('\n\n\n')

  

