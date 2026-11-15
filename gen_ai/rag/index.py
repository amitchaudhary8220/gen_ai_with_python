from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)
from openai import vector_stores

pdf_path = Path(__file__).parent / "nodejs.pdf"

# Load this file in python program

loader = PyPDFLoader(file_path=pdf_path)
docs = []
docs_lazy = loader.lazy_load()

for doc in docs_lazy:
    docs.append(doc)
# print(docs[0].page_content[:100])
# print(docs[0].metadata)


# Split the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)

chunks = text_splitter.split_documents(documents=docs)

# Vector embedding
embedding_model = OllamaEmbeddings(model="bge-m3")

# Vector store
vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning_rag",
)

print("Indexing of document done")
