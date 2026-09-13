import logging
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import router as api_router
from app.config import settings
from app.logging_config import setup_logging
from app.utils import check_chroma_heartbeat, limiter

# Configure structured enterprise logging
is_prod: bool = settings.ENVIRONMENT.lower() == "production"
setup_logging(use_json=is_prod)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle events.

    Pre-loads vector index and fallback chat engine into application state
    during container boot to eliminate cold-start latency.
    """
    provider_desc = (
        f"Local (Ollama: {settings.OLLAMA_MODEL})"
        if settings.LLM_PROVIDER.lower() == "ollama"
        else f"Cloud (Groq: {settings.LLM_MODEL})"
    )
    logger.info(f"Initializing AI Engine [{provider_desc}] and Vector DB connection...")

    try:
        from app.engine import get_chat_engine, get_vector_index

        # Store pre-warmed read-only index in app.state
        app.state.vector_index = get_vector_index()
        app.state.chat_engine = get_chat_engine(index=app.state.vector_index)
        logger.info(f"AI Engine successfully initialized in [{provider_desc}] mode.")
    except Exception as e:
        logger.error(f"Failed to initialize AI Engine during startup: {e}")
        app.state.vector_index = None
        app.state.chat_engine = None

    yield

    logger.info("Application shutdown initiated. Cleaning resources...")


# Restrict schema introspection endpoints in production environments
docs_path = "/docs" if not is_prod else None
redoc_path = "/redoc" if not is_prod else None
openapi_path = "/openapi.json" if not is_prod else None

app = FastAPI(
    title="Legal Chatbot RAG API",
    description="Production-grade Statutory Legal Assistant API supporting dual-mode LLM inference (Ollama & Groq).",
    version="1.2.0",
    docs_url=docs_path,
    redoc_url=redoc_path,
    openapi_url=openapi_path,
    lifespan=lifespan,
)

# Register Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

try:
    from llama_index.core import set_global_handler

    set_global_handler("simple")
except ImportError:
    pass

# Include API Router
app.include_router(api_router)


@app.get("/")
@limiter.limit("10/minute")
def root(request: Request) -> dict[str, str]:
    """Root status endpoint returning service identity and runtime configuration.

    Args:
        request: Incoming FastAPI Request object.

    Returns:
        dict[str, str]: Service status and model metadata.
    """
    active_model = (
        settings.OLLAMA_MODEL
        if settings.LLM_PROVIDER.lower() == "ollama"
        else settings.LLM_MODEL
    )
    return {
        "message": "Legal Chatbot API is running securely!",
        "provider": settings.LLM_PROVIDER,
        "model": active_model,
        "environment": settings.ENVIRONMENT,
        "status": "ready",
    }


@app.get("/health")
def health_check(request: Request) -> Any:
    """Readiness and liveness health probe endpoint for container orchestrators.

    Probes the vector store index readiness and ChromaDB HTTP connectivity.

    Args:
        request: Incoming FastAPI Request object.

    Returns:
        JSONResponse or dict: Health payload with HTTP 200 (healthy) or 503 (degraded).
    """
    has_index = getattr(request.app.state, "vector_index", None) is not None
    has_engine = getattr(request.app.state, "chat_engine", None) is not None
    is_engine_ready = has_index or has_engine

    if not is_engine_ready:
        try:
            from app.engine import get_chat_engine, get_vector_index

            request.app.state.vector_index = get_vector_index()
            request.app.state.chat_engine = get_chat_engine(
                index=request.app.state.vector_index
            )
            is_engine_ready = True
        except Exception:
            is_engine_ready = False

    is_chroma_alive = check_chroma_heartbeat(
        settings.CHROMA_HOST, settings.CHROMA_PORT
    )

    all_healthy = is_engine_ready and is_chroma_alive
    status_code = 200 if all_healthy else 503

    provider_name = settings.LLM_PROVIDER.lower().strip()
    active_model = (
        settings.OLLAMA_MODEL if provider_name == "ollama" else settings.LLM_MODEL
    )

    payload = {
        "status": "healthy" if all_healthy else "degraded",
        "provider": provider_name,
        "model": active_model,
        "environment": settings.ENVIRONMENT,
        "components": {
            "ai_engine": "ready" if is_engine_ready else "not_ready",
            "chroma_db": "connected" if is_chroma_alive else "unreachable",
        },
        "service": "Legal Chatbot RAG API",
    }

    if not all_healthy:
        return JSONResponse(status_code=status_code, content=payload)
    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
