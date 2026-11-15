import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Copies the KEY=value lines from .env into os.environ (like require("dotenv").config()).
load_dotenv()

# Inception Labs speaks the same API as OpenAI, so the OpenAI SDK works:
# we just point it at Inception's URL and give it Inception's key.
client = OpenAI(
    base_url="https://api.inceptionlabs.ai/v1",
    api_key=os.getenv("INCEPTION_API_KEY"),
)

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%c+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"Weather in {city}: {response.text}"
    return f"Sorry, I couldn't fetch weather information for {city}."

def main():
    user_query = input("> ")

    response = client.chat.completions.create(
        model=os.getenv("INCEPTION_MODEL", "mercury-2.5"),
        messages=[
            {"role": "user", "content": user_query},
        ],
    ) 
    print(f"🤖 {response.choices[0].message.content}")

# main()

print(get_weather("goa"))
