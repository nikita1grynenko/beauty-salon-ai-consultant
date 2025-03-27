from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from load_docs import load_documents
from dotenv import load_dotenv
import os

load_dotenv()

def build_vector_store():
    docs = load_documents("data/faq.txt")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(docs, embedding=embeddings, persist_directory="db")
    vectorstore.persist()
    print("Векторна база створена й збережена")

if __name__ == "__main__":
    build_vector_store()
