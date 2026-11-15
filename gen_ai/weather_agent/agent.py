# cot - chain of thought prompting : This is a more advanced form of prompting, where you ask the model to perform a task by providing it with a series of steps or instructions. This can help the model to better understand the task and generate more accurate responses.

import json
import os
import subprocess
from typing import Literal

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# Copies the KEY=value lines from .env into os.environ (like require("dotenv").config()).
load_dotenv()

# Both providers speak the same API as OpenAI, so the OpenAI SDK works for both:
# we just point it at a different URL, key and model.
PROVIDERS = {
    # Local Qwen running in Ollama on this Mac. Ollama ignores the key, but the SDK needs one.
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "qwen3:4b-instruct",
    },
    # Inception Labs (Mercury) in the cloud, needs INCEPTION_API_KEY in .env.
    "inception": {
        "base_url": "https://api.inceptionlabs.ai/v1",
        "api_key": os.getenv("INCEPTION_API_KEY"),
        "model": os.getenv("INCEPTION_MODEL", "mercury-2.5"),
    },
}

# Change this (or set LLM_PROVIDER=inception in .env) to switch models.
PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
config = PROVIDERS[PROVIDER]

client = OpenAI(
    base_url=config["base_url"],
    api_key=config["api_key"],
)
MODEL = config["model"]

# Which OpenAI API to call: "chat" (Chat Completions) or "responses" (Responses API).
# Change this (or set LLM_API=responses in .env) to compare the two.
API_MODE = os.getenv("LLM_API", "chat")


def run_command(cmd: str) -> str:
    # os.system only returns the exit status (0, 256, ...) and prints the output to the
    # terminal, so the model never saw it. subprocess.run with capture_output=True gives
    # us stdout/stderr back as strings (like child_process.exec's callback in Node).
    # check=False: a failing command shouldn't crash the agent; we pass the exit code to the model.
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    return f"exit code {result.returncode}\n{output}"


def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%c+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"Weather in {city}: {response.text}"
    return f"Sorry, I couldn't fetch weather information for {city}."


available_tools = {"get_weather": get_weather, "run_command": run_command}

SYSTEM_PROMPT = """
   You're an expert AI Assistant in resolving user queries using chain of thought. 
   You work on START, PLAN and OUTPUT steps.
   You need to first plan that what needs to be done. The plan can be multiple steps.
   One you think enough polan has been done, finally you can give an output.
   You can also call a tool if required from the list of available tools.
   for every tool call wait for the observer step which is the output from the called tool.

   Rules:
   - Strictly follow the output in JSON format

   - Only run one step at a time.
   - The sequence of steps is START (where user gives an input), PLAN (That can be multiple steps), and finally OUTPUT(which is going to the displayed to the user).
   - For any weather question you MUST send a TOOL step. Never guess or invent weather data.
   - After a TOOL step, stop. The system will reply with an OBSERVE message containing the real tool result. Never write OBSERVE yourself.
   - Never say you got information from a tool unless you have received its OBSERVE message.
   - The OUTPUT step must contain the final answer with the real data from OBSERVE (e.g. the temperature), not a plan.
   - In a TOOL step, "tool" is the tool's name and "input" is the VALUE to pass to it (a city name, or the full shell command). Never put the tool's name in "input".

   Output JSON Format:
    {"step": "START" | "PLAN" | "TOOL" | "OUTPUT", "content": "string", "tool": "string", "input": "string"}

   Available Tools:
   - get_weather(city: str): Takes city name as input string and returns the weather info about the city.
   - run_command(cmd: str): Runs ONE shell command on the user's Mac (macOS, zsh) and returns its exit code and output. "input" must be the complete command itself, e.g. "mkdir -p /Users/someone/projects/demo" or "ls -la /Users/someone".

   Example 1:
        START: Hey, Can you solve 2 + 3 * 5 / 10
        PLAN: {"step": "PLAN", "content": "Seems like user is interested in maths problem."},
        PLAN: {"step": "PLAN", "content": "Looking at the problem, we should it with BODMAS rule."},
        PLAN: {"step": "PLAN", "content": "Yes BODMAS seems right choice for this problem."},
        PLAN: {"step": "PLAN", "content": "So, we first solve 3 * 5 = 15, "},
        PLAN: {"step": "PLAN", "content": "Then we do 15 / 10 = 1.5, "},
        PLAN: {"step": "PLAN", "content": "Then we do 2 + 1.5 = 3.5, "},
        OUTPUT: {"step": "OUTPUT", "content": "The result of the expression 2 + 3 * 5 / 10 is 3.5."}

   Example 2:
       START: What is the weather of Delhi?
       PLAN: {"step": "PLAN", "content": "Seems like user is interested in getting the weather information of Delhi in India."},
       PLAN: {"step": "PLAN", "content": "Lets see if we have any available tool from the list of available tools."},
       PLAN: {"step": "PLAN", "content": "Great, We have the get_weather tool available for this query."},
       PLAN: {"step": "PLAN", "content": "I need to call get_weather tool for delhi as input for city."},
       TOOL: {"step": "TOOL", "tool": "get_weather", "input": "delhi"},
       OBSERVE (sent by the system, not by you): {"step": "OBSERVE", "tool": "get_weather", "output": "Weather in delhi: ☁️ +30°C"},
       PLAN: {"step": "PLAN", "content": "Great, I got the weather information of delhi from the get_weather tool."},
       OUTPUT: {"step": "OUTPUT", "content": "The current weather in Delhi is cloudy with a temperature of 30 degrees Celsius with some humidity."}

   Example 3:
       START: Create a folder named reports in /Users/someone/projects
       PLAN: {"step": "PLAN", "content": "The user wants a new folder. The run_command tool can do this with mkdir."},
       PLAN: {"step": "PLAN", "content": "The full command is: mkdir -p /Users/someone/projects/reports"},
       TOOL: {"step": "TOOL", "tool": "run_command", "input": "mkdir -p /Users/someone/projects/reports"},
       OBSERVE (sent by the system, not by you): {"step": "OBSERVE", "tool": "run_command", "output": "exit code 0"},
       PLAN: {"step": "PLAN", "content": "Exit code 0 means the command succeeded."},
       OUTPUT: {"step": "OUTPUT", "content": "Done! I created the folder /Users/someone/projects/reports."}

"""


class MyOutputFormat(BaseModel):
    # Literal = only these exact values are allowed (like a TS union type "START" | "PLAN" | ...).
    step: Literal["START", "PLAN", "TOOL", "OUTPUT"] = Field(
        ..., description="The ID of the step"
    )
    content: str | None = Field(
        None, description="The optional string content for the step"
    )
    tool: str | None = Field(
        None, description="TOOL step only: the tool's name, e.g. 'get_weather' or 'run_command'"
    )
    # These descriptions go into the JSON Schema the model sees, so be precise.
    input: str | None = Field(
        None,
        description="TOOL step only: the value passed to the tool, e.g. 'delhi' for get_weather "
        "or 'mkdir -p /path/to/folder' for run_command. Never the tool's name.",
    )
    output: str | None = Field(
        None, description="The output from the tool (if applicable)"
    )


def next_step(message_history) -> MyOutputFormat:
    """Ask the model for its next step. Always returns a parsed step, never None."""
    if API_MODE == "responses":
        response = client.responses.parse(
            model=MODEL,
            input=message_history,
            text_format=MyOutputFormat,
        )
        parsed = response.output_parsed
    else:
        response = client.chat.completions.parse(
            model=MODEL,
            response_format=MyOutputFormat,
            messages=message_history,
        )
        parsed = response.choices[0].message.parsed

    # The one place we handle "model didn't give valid JSON" — after this, it's never None.
    if parsed is None:
        raise ValueError("Model reply didn't match MyOutputFormat")
    return parsed


message_history = [{"role": "system", "content": SYSTEM_PROMPT}]


print("\n\n\n")
while True:
    user_query = input("👉🏻...")
    message_history.append({"role": "user", "content": user_query})

    while True:
        # next_step returns ONE object (a MyOutputFormat), so take it as one variable.
        parsed_message: MyOutputFormat = next_step(message_history)
        # Turn the model back into a JSON string for the history (like JSON.stringify),
        # leaving out the fields that are None.
        assistant_message = parsed_message.model_dump_json(exclude_none=True)
        print(
            f" assistant_message  {assistant_message}  and parsed_message is ---->>>  {parsed_message}"
        )
        message_history.append({"role": "assistant", "content": assistant_message})

        if parsed_message.step == "START":
            print("🔥", parsed_message.content)
            # Qwen replies with an empty string if the last message is its own, so nudge it.
            message_history.append({"role": "user", "content": "Next step."})
            continue  # Skip the rest of the loop and go to the next iteration to get the assistant's response after START step

        if parsed_message.step == "TOOL":
            tool_to_call = parsed_message.tool
            tool_input = parsed_message.input
            print(f"🛠️ Calling tool: {tool_to_call} with input: {tool_input}")
            # tool and input are "str | None" in MyOutputFormat, and the model might also
            # name a tool we don't have. Tell the model instead of crashing.
            # `not x` is True for both None and "" (the model sends "" for unused fields).
            if not tool_to_call or tool_to_call not in available_tools:
                tool_output = f"Error: unknown tool {tool_to_call!r}. Available tools: {list(available_tools)}"
            elif not tool_input or tool_input in available_tools:
                # Empty input, or the tool's name sent as the input (the mistake in your log).
                tool_output = (
                    f"Error: invalid input {tool_input!r}. 'input' must be the value to pass to "
                    f"{tool_to_call}, e.g. a city name or the full shell command, not a tool name."
                )
            else:
                tool_output = available_tools[tool_to_call](tool_input)
            print(f"🛠️ {tool_to_call} ({tool_input}) = {tool_output}")
            message_history.append(
                {
                    "role": "developer",
                    "content": json.dumps(
                        {"step": "OBSERVE", "tool": tool_to_call, "output": tool_output}
                    ),
                }
            )
            continue  # Skip the rest of the loop and go to the next iteration to get the assistant's response after tool call
        if parsed_message.step == "PLAN":
            print("🧠", parsed_message.content)
            # Same nudge as after START: give Qwen a user turn to answer.
            message_history.append({"role": "user", "content": "Next step."})
            continue  # Skip the rest of the loop and go to the next iteration to get the assistant's response after PLAN step

        if parsed_message.step == "OUTPUT":
            print("✅", parsed_message.content)
            break


print("\n\n\n")
