import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # API Keys (Required in production)
    GROQ_API_KEY: str = Field(..., description="Groq Cloud API key for LLM inference")
    APP_API_KEY: str = Field(..., description="Secret key required for X-API-Key header authentication")

    # Models
    LLM_MODEL: str = Field(default="llama-3.3-70b-versatile")
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-small-en-v1.5")
    RERANKER_MODEL: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")

    # ChromaDB
    CHROMA_HOST: str = Field(default="chromadb")
    CHROMA_PORT: int = Field(default=8000)

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def raw_data_dir(self) -> str:
        return os.path.join(self.BASE_DIR, "Data", "raw")

settings = Settings()
