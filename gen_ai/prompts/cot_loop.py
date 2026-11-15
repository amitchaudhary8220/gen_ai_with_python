# cot_loop - same chain of thought prompt as cot.py, but in a loop:
# each API call returns ONE step, we add it to the history and ask again,
# until the model says "OUTPUT".

import json
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
   You're an expert AI Assistant in resolving user queries using chain of thought.
   You work on START, PLAN and OUTPUT steps.
   You need to first plan what needs to be done. The plan can be multiple steps.
   Once you think enough planning has been done, finally you can give an output.

   Rules:
   - Strictly follow the output in JSON format.
   - Only run one step at a time. Return exactly ONE JSON object per reply.
   - Always do at least 2 PLAN steps before the OUTPUT step, even for easy questions.
   - The sequence of steps is START (where user gives an input), PLAN (that can be multiple steps), and finally OUTPUT (which is going to be displayed to the user).

   Output JSON Format:
    {"step": "START" | "PLAN" | "OUTPUT", "content": "string"}

   Example:
   START: Hey, Can you solve 2 + 3 * 5 / 10
   PLAN: {"step": "PLAN", "content": "Seems like user is interested in maths problem."}
   PLAN: {"step": "PLAN", "content": "Looking at the problem, we should solve it with BODMAS rule."}
   PLAN: {"step": "PLAN", "content": "So, we first solve 3 * 5 = 15"}
   PLAN: {"step": "PLAN", "content": "Then we do 15 / 10 = 1.5"}
   PLAN: {"step": "PLAN", "content": "Then we do 2 + 1.5 = 3.5"}
   OUTPUT: {"step": "OUTPUT", "content": "The result of the expression 2 + 3 * 5 / 10 is 3.5."}
"""

STEP_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "step",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "step": {"type": "string", "enum": ["START", "PLAN", "OUTPUT"]},
                "content": {"type": "string"},
            },
            "required": ["step", "content"],
            "additionalProperties": False,
        },
    },
}

user_query = input("Ask something: ")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_query},
]

# Safety limit so a confused model can't loop forever (and burn API credits).
for _ in range(15):
    response = client.chat.completions.create(
        model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
        # A JSON schema makes the API itself enforce {"step", "content"},
        # instead of just hoping the model follows the prompt.
        response_format=STEP_SCHEMA,
        messages=messages,
    )

    raw = response.choices[0].message.content
    # Feed the model's own step back in, so next call it knows what it already did.
    messages.append({"role": "assistant", "content": raw})

    step = json.loads(raw)

    if step.get("step") == "OUTPUT":
        print(f"\n🤖 {step['content']}")
        break

    print(f"🧠 {step.get('step')}: {step.get('content')}")
