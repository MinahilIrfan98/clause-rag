from pathlib import Path
from functools import lru_cache
from pydantic_settings import SettingsConfigDict, BaseSettings

from langchain.embeddings import init_embeddings  # Embeddings
from langchain_core.embeddings import Embeddings    
from qdrant_client import QdrantClient


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"  # api/.env

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix = "RAG_",
        env_file=ENV_FILE,
        extra = "ignore",)

    #app
    app_name: str = "Clause Shop Assistant"
    data_path: str = "data/shop_handbook.pdf"

    #chat
    chat_model: str = "gemma3:1b"
    chat_provider: str = "ollama"
    chat_temperature: float = 0.1

    #embedding
    embed_model: str = "nomic-embed-text:latest"
    embed_provider: str = "ollama"
    embed_dim: int = 768

    #indexing 
    chunk_size: int = 600
    chunk_overlap: int = 100

    #retrieval
    top_k: int = 3

    #Qdrant
    collection: str = "shop_handbook" #table
    qdrant_data: str = "./qdrant_data" #vector store

    #prompt
    system_prompt: str = (
        "You are a helpful Clause shop assistant. "
        "Answers only from provided context. "
    )

@lru_cache
def get_settings():
    return Settings()

def get_embeddings(settings: Settings) -> Embeddings:
    return init_embeddings(
        model=settings.embed_model,
        provider=settings.embed_provider
    )
def get_qdrant_client(settings: Settings):
    return QdrantClient(
        #collection_name=settings.collection,
        path=settings.qdrant_data
    )