import os
import sys
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter

# Увімкнути UTF-8 у Windows-терміналі (для кирилиці)
if sys.platform.startswith('win'):
    os.system('chcp 65001')

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

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)
