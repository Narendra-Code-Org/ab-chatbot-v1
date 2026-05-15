from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    ollama_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gpt-oss:20b"
    
    qdrant_url: str = ""
    qdrant_api_key: str = ""



settings = Settings()                                                     