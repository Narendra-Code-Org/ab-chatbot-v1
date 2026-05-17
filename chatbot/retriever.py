import os
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
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
    else:
        # Local fallback (using local Qdrant if available, or error if not configured)
        client = QdrantClient(path="local_qdrant_db")
    
    # Ensure the collection exists in Qdrant
    try:
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    except Exception as e:
        print(f"Error checking/creating collection '{collection_name}': {e}")
        
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )

def get_retriever(collection_name: str):
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

