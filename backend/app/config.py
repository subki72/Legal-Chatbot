import os
from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Enforce stable HuggingFace and LlamaIndex cache configurations
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
if "LLAMA_INDEX_CACHE_DIR" not in os.environ and os.path.exists("/home/appuser/.cache"):
    os.environ["LLAMA_INDEX_CACHE_DIR"] = "/home/appuser/.cache/llama_index"


class Settings(BaseSettings):
    """Application configuration and environment variable loader.

    Validates configuration parameters for operational environments, LLM providers,
    vector storage, and security credentials.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Operational Environment
    ENVIRONMENT: str = Field(
        default="production",
        description="Operating environment: 'production', 'staging', or 'development'."
    )
    ALERT_WEBHOOK_URL: Optional[str] = Field(
        default=None,
        description="Incoming webhook URL for incident notifications (Slack/Discord/Telegram)."
    )

    # LLM Provider Switch ("ollama" or "groq")
    LLM_PROVIDER: str = Field(
        default="ollama",
        description="Active LLM provider: 'ollama' (local) or 'groq' (cloud)."
    )

    # Security & Authentication
    APP_API_KEY: str = Field(
        ...,
        description="Secret key required for X-API-Key header authentication."
    )

    # Cloud Provider Config (Groq)
    GROQ_API_KEY: Optional[str] = Field(
        default=None,
        description="Groq Cloud API key (required when LLM_PROVIDER is set to 'groq')."
    )
    LLM_MODEL: str = Field(
        default="llama-3.3-70b-versatile",
        description="Active cloud LLM model identifier."
    )

    # Local Provider Config (Ollama)
    OLLAMA_BASE_URL: str = Field(
        default="http://host.docker.internal:11434",
        description="Ollama server base endpoint URL."
    )
    OLLAMA_MODEL: str = Field(
        default="qwen2.5:7b",
        description="Local Ollama model identifier."
    )
    OLLAMA_TIMEOUT: float = Field(
        default=300.0,
        description="HTTP request timeout to Ollama in seconds (300s recommended for CPU inference)."
    )

    # Embedding & Reranker
    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="HuggingFace embedding model identifier."
    )
    RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder reranker model identifier."
    )
    USE_RERANKER: bool = Field(
        default=False,
        description="Flag to enable cross-encoder reranking when cached locally."
    )

    # ChromaDB
    CHROMA_HOST: str = Field(
        default="chromadb",
        description="Hostname or IP address for the ChromaDB vector database service."
    )
    CHROMA_PORT: int = Field(
        default=8000,
        description="Port number for the ChromaDB service."
    )

    # Project Base Path
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def raw_data_dir(self) -> str:
        """Resolve the absolute directory path containing raw input documents.

        Returns:
            str: Absolute path to the raw data directory.
        """
        return os.path.join(self.BASE_DIR, "Data", "raw")

    @model_validator(mode="after")
    def validate_provider_credentials(self) -> "Settings":
        """Validate that necessary credentials exist for the selected LLM provider.

        Returns:
            Settings: Validated configuration settings instance.

        Raises:
            ValueError: If cloud provider is selected but API key is missing.
        """
        provider = self.LLM_PROVIDER.lower().strip()
        if provider == "groq" and not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER is set to 'groq'.")
        return self


settings = Settings()
