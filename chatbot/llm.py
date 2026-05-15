from langchain_ollama import OllamaLLM
from config import settings

def get_llm():
    return OllamaLLM(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model
    )
