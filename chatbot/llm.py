import boto3
from langchain_aws import ChatBedrockConverse
from config import settings

def get_llm():
    aws_kwargs = {}
    if settings.aws_access_key_id:
        aws_kwargs["aws_access_key_id"] = settings.aws_access_key_id
    if settings.aws_secret_access_key:
        aws_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.aws_session_token:
        aws_kwargs["aws_session_token"] = settings.aws_session_token
    if settings.aws_region:
        aws_kwargs["region_name"] = settings.aws_region

    if aws_kwargs:
        session = boto3.Session(**aws_kwargs)
        client = session.client("bedrock-runtime")
    else:
        # Fallback to default credentials
        client = boto3.client("bedrock-runtime")

    return ChatBedrockConverse(
        client=client,
        model_id=settings.bedrock_llm_model_id
    )
