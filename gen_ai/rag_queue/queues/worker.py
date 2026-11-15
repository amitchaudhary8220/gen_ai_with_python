import os

from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()

embedding_model = OllamaEmbeddings(model="bge-m3")


vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model,
)

client = OpenAI(
    api_key=os.environ["INCEPTION_API_KEY"], base_url="https://api.inceptionlabs.ai/v1"
)


def process_query(query: str):
    print("Searching Chunks", query)

    # Relevant chunks form the vector db
    search_results = vector_db.similarity_search(query=query)

    context = "\n\n\n".join(
        [
            f"Page Content: {result.page_content} \nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}"
            for result in search_results
        ]
    )

    SYSTEM_PROMPT = f"""
        You are a helpfull AI Assistant who answers user query based on the avaiable context retrieved from a PDF file along wiht page_contents and page number.

        You should only ans the user based on the following context and navigate the user to opne the right page number to know more.

        Context:
        {context}
        """
    response = client.chat.completions.create(
        model="mercury-3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        max_completion_tokens=8192,
    )

    print(f"🤖: {response.choices[0].message.content}")
    return response.choices[0].message.content
