import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    APP_API_KEY: str = Field(default="sk-legal-assistant-default-key-123", env="APP_API_KEY") # Dummy default for local dev

    # Models
    LLM_MODEL: str = Field(default="llama-3.3-70b-versatile", env="LLM_MODEL")
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-small-en-v1.5", env="EMBEDDING_MODEL")
    RERANKER_MODEL: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", env="RERANKER_MODEL")

    # ChromaDB
    CHROMA_HOST: str = Field(default="chromadb", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def raw_data_dir(self) -> str:
        return os.path.join(self.BASE_DIR, "Data", "raw")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
