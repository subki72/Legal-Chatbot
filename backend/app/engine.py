import logging
import os
from typing import Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a professional AI Legal Assistant specializing in Indonesian statutory law. "
    "Answer the user query strictly based on the provided statutory context documents. "
    "Specifically cite the legal grounds (Articles and Paragraphs / Pasal dan Ayat). "
    "Respond in formal Indonesian as appropriate for legal consultation. "
    "If the answer is not present in the provided context, explicitly state that the information is not available."
)


def get_llm() -> Any:
    """Factory method to instantiate the LLM client based on configured provider.

    Instantiates either a local Ollama client or a cloud Groq client based on
    the `LLM_PROVIDER` environment configuration.

    Returns:
        Any: Configured LlamaIndex LLM instance.

    Raises:
        ImportError: If the required provider library is not installed.
        ValueError: If provider is unrecognized or required credentials are missing.
    """
    provider = settings.LLM_PROVIDER.lower().strip()

    if provider == "ollama":
        try:
            # Compatibility patch between ollama Python SDK and llama-index-llms-ollama
            from ollama._types import ChatResponse
            ChatResponse.model_config["extra"] = "allow"
            ChatResponse.model_rebuild(force=True)
        except Exception:
            pass

        try:
            from llama_index.llms.ollama import Ollama
        except ImportError:
            raise ImportError(
                "Package 'llama-index-llms-ollama' is not installed. "
                "Install it with: pip install llama-index-llms-ollama"
            )
        logger.info(
            f"Using Local Ollama LLM: {settings.OLLAMA_MODEL} @ {settings.OLLAMA_BASE_URL}"
        )
        return Ollama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=settings.OLLAMA_TIMEOUT,
        )

    elif provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER is set to 'groq'.")
        try:
            from llama_index.llms.groq import Groq
        except ImportError:
            raise ImportError(
                "Package 'llama-index-llms-groq' is not installed. "
                "Install it with: pip install llama-index-llms-groq"
            )
        logger.info(f"Using Cloud Groq LLM: {settings.LLM_MODEL}")
        return Groq(
            model=settings.LLM_MODEL,
            api_key=settings.GROQ_API_KEY,
        )

    else:
        raise ValueError(
            f"LLM Provider '{settings.LLM_PROVIDER}' is not recognized. "
            "Valid options are 'ollama' or 'groq'."
        )


def get_vector_index() -> Any:
    """Connect to ChromaDB and initialize a thread-safe VectorStoreIndex.

    Reuses the persistent ChromaDB collection 'legal_docs' and configures
    the HuggingFace embedding model with local cache resolution.

    Returns:
        VectorStoreIndex: Initialized vector store index ready for retrieval.

    Raises:
        ImportError: If vector store or embedding dependencies are missing.
        ValueError: If connection to ChromaDB fails.
    """
    try:
        import chromadb
        from llama_index.core import VectorStoreIndex
        from llama_index.vector_stores.chroma import ChromaVectorStore
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    except ImportError as e:
        logger.error(f"Vector Store dependencies not installed: {e}")
        raise

    try:
        db = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        chroma_collection = db.get_or_create_collection("legal_docs")
    except Exception as e:
        logger.error(f"Failed to access ChromaDB collection: {e}")
        raise ValueError(f"ChromaDB error: {e}")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Resolve persistent model cache directory
    cache_dir: Optional[str] = None
    for candidate in [
        "/home/appuser/.cache/huggingface/hub",
        os.path.expanduser("~/.cache/huggingface/hub"),
    ]:
        if os.path.exists(candidate):
            cache_dir = candidate
            break

    # If the model is already downloaded locally, prevent slow HuggingFace network checks
    is_cached = False
    if cache_dir:
        model_slug = f"models--{settings.EMBEDDING_MODEL.replace('/', '--')}"
        if os.path.exists(os.path.join(cache_dir, model_slug)):
            is_cached = True

    embed_model = HuggingFaceEmbedding(
        model_name=settings.EMBEDDING_MODEL,
        cache_folder=cache_dir,
        model_kwargs={"local_files_only": True} if is_cached else {},
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    return index


def get_chat_engine(index: Optional[Any] = None, llm: Optional[Any] = None) -> Any:
    """Construct an isolated RAG chat engine instance for concurrent query execution.

    Creates a request-scoped engine instance to prevent race conditions during
    asynchronous query processing.

    Args:
        index: Optional pre-loaded VectorStoreIndex instance.
        llm: Optional pre-configured LLM client instance.

    Returns:
        BaseChatEngine: Configured conversational retrieval engine.
    """
    if index is None:
        index = get_vector_index()

    if llm is None:
        llm = get_llm()

    node_postprocessors: list[Any] = []
    similarity_top_k = 3 if settings.LLM_PROVIDER.lower() == "ollama" else 5

    if getattr(settings, "USE_RERANKER", False):
        try:
            from llama_index.core.postprocessor import SentenceTransformerRerank
            reranker = SentenceTransformerRerank(
                model=settings.RERANKER_MODEL, top_n=3
            )
            node_postprocessors.append(reranker)
            similarity_top_k = 8
            logger.info("Reranker model enabled successfully (top_n=3, similarity_top_k=8).")
        except Exception as e:
            logger.warning(
                f"Reranker model could not be loaded ({e}); falling back to default similarity_top_k."
            )

    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        node_postprocessors=node_postprocessors,
        similarity_top_k=similarity_top_k,
        system_prompt=SYSTEM_PROMPT,
    )

    return chat_engine
