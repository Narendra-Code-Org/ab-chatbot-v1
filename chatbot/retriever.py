import os
import logging
import boto3
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_aws import BedrockEmbeddings
from config import settings

logger = logging.getLogger("ab-chatbot.retriever")

def get_embeddings():
    aws_kwargs = {}
    if settings.aws_access_key_id:
        aws_kwargs["aws_access_key_id"] = settings.aws_access_key_id
    if settings.aws_secret_access_key:
        aws_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.aws_session_token:
        aws_kwargs["aws_session_token"] = settings.aws_session_token
    if settings.aws_region:
        aws_kwargs["region_name"] = settings.aws_region

    try:
        if aws_kwargs:
            session = boto3.Session(**aws_kwargs)
            client = session.client("bedrock-runtime")
        else:
            # Fallback to default credentials from AWS environment/config profiles
            client = boto3.client("bedrock-runtime")

        return BedrockEmbeddings(
            client=client,
            model_id=settings.bedrock_embeddings_model_id,
            dimensions=512
        )
    except Exception as e:
        logger.error(f"Failed to initialize BedrockEmbeddings client: {e}", exc_info=True)
        raise e

# Initialize embeddings singleton
embeddings = get_embeddings()

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
    
    # Ensure the collection exists in Qdrant and matches dimensions
    target_dim = 512
    try:
        if not client.collection_exists(collection_name):
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=target_dim, distance=Distance.COSINE)
            )
            logger.info(f"Created collection '{collection_name}' with dimension {target_dim}")
        else:
            # Check existing collection configuration to verify dimension size
            collection_info = client.get_collection(collection_name)
            
            # Safe parsing of dimension configuration
            if hasattr(collection_info.config.params.vectors, 'size'):
                existing_dim = collection_info.config.params.vectors.size
            elif isinstance(collection_info.config.params.vectors, dict) and 'size' in collection_info.config.params.vectors:
                existing_dim = collection_info.config.params.vectors['size']
            else:
                existing_dim = None
                
            if existing_dim != target_dim:
                logger.warning(
                    f"Collection '{collection_name}' has dimension {existing_dim}, "
                    f"but model uses {target_dim}. Re-creating collection to prevent model incompatibility."
                )
                client.delete_collection(collection_name)
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=target_dim, distance=Distance.COSINE)
                )
                logger.info(f"Successfully re-created collection '{collection_name}' with size {target_dim}.")
    except Exception as e:
        logger.error(f"Error checking/creating collection '{collection_name}': {e}", exc_info=True)
        raise e
        
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )

def get_retriever(collection_name: str):
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.as_retriever(search_kwargs={"k": 3})
