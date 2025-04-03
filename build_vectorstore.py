from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from load_docs import load_documents
from dotenv import load_dotenv

load_dotenv()


def build_vector_store():
    documents = load_documents("data")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embedding=embeddings, persist_directory="db")
    vectorstore.persist()
    print("Векторна база створена і збережена")


if __name__ == "__main__":
    build_vector_store()
