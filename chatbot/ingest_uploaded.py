import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chatbot.retriever import get_vectorstore

UPLOADED_COLLECTION = "uploaded_docs"

def ingest_uploaded_doc(filepath: str):
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    
    vectorstore = get_vectorstore(UPLOADED_COLLECTION)
    vectorstore.add_documents(chunks)
