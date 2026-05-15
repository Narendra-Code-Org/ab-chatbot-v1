import os
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_vectorstore(collection_name: str):
    if settings.qdrant_url and settings.qdrant_api_key:
        # Production: Qdrant Cloud
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
    else:
        # Local fallback (using local Qdrant if available, or error if not configured)
        # Note: If they want truly local, they'd run Qdrant in docker.
        # For this migration, we assume cloud is the goal.
        client = QdrantClient(path="local_qdrant_db")
        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

def get_retriever(collection_name: str):
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.as_retriever(search_kwargs={"k": 3})
