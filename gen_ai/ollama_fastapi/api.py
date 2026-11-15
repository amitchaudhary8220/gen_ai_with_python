from fastapi import FastAPI,Body
from ollama import Client
app = FastAPI()

client = Client(
    host = 'http://localhost:11434'
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/chat")
def chat(
        message: str = Body(...,description="The message to send to the model")  
):
  response =  client.chat(
        model = "qwen3:4b-instruct",
        messages = [
            {"role": "user", "content": message}
        ],
        think =  False,
        options = {
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9, 
        }
    )

  return {"response": response.message.content}
