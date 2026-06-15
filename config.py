from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    ollama_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss:20b"
    
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    aws_region: str = "us-east-1"
    bedrock_embeddings_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_llm_model_id: str = "google.gemma-3-4b-it"


settings = Settings()