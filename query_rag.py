from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
from logger import log_query

load_dotenv()

def query_bot(user_query: str):
    db = Chroma(persist_directory="db", embedding_function=OpenAIEmbeddings())
    results = db.similarity_search(user_query, k=3)
    context = "\n---\n".join([doc.page_content for doc in results])

    system_prompt = f"""
Ти — ввічливий асистент салону краси. Використовуй лише контекст нижче для відповіді на запит.

Контекст:
{context}
"""

    chat = ChatOpenAI(temperature=0.3, model_name="gpt-4o")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]
    response = chat(messages)
    return response.content

if __name__ == "__main__":
    while True:
        query = input("Клієнт: ")
        if query.lower() in ["вихід", "exit"]:
            break
        log_query(query, source="query_direct")
        print("Бот:", query_bot(query))
