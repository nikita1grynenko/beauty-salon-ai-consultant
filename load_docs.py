from langchain.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os

def load_documents(path: str):
    docs = []

    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)

        if filename.endswith(".txt"):
            loader = TextLoader(full_path, encoding='utf-8')
            docs.extend(loader.load())

        elif filename.endswith(".pdf"):
            loader = PyMuPDFLoader(full_path)
            docs.extend(loader.load())

        # Можна додати підтримку .md, .docx, .csv

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)
