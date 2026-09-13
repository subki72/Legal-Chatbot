import json
import logging
import time
import urllib.request
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from app.config import settings
from app.utils import estimate_tokens, format_source_citations, limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# API Key Security Header Scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def dispatch_webhook_alert(title: str, message: str, severity: str = "ERROR") -> None:
    """Dispatch operational incident alert notifications to an external webhook.

    Sends structured alerts to configured Slack, Discord, or Telegram webhooks
    with non-blocking execution and a short timeout.

    Args:
        title: Short title summarizing the incident event.
        message: Detailed error or diagnostic context string.
        severity: Incident severity level ('INFO', 'WARNING', 'ERROR', 'CRITICAL').
    """
    webhook_url: Optional[str] = getattr(settings, "ALERT_WEBHOOK_URL", None)
    if not webhook_url:
        return

    payload = {
        "content": (
            f"[{severity}] Legal Chatbot Incident Alert\n"
            f"Event: {title}\n"
            f"Detail: `{message[:300]}`\n"
            f"Metadata: `Env: {settings.ENVIRONMENT} | Provider: {settings.LLM_PROVIDER}`"
        )
    }
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "LegalChatbot-Alerter/1.0",
            },
        )
        urllib.request.urlopen(req, timeout=4)
    except Exception as e:
        logger.warning(f"Failed to dispatch incident webhook alert: {e}")


async def get_api_key(header_value: Optional[str] = Security(api_key_header)) -> str:
    """Validate incoming request authorization via the X-API-Key header.

    Args:
        header_value: Raw value extracted from the X-API-Key header.

    Returns:
        str: Validated API key string.

    Raises:
        HTTPException: 403 Forbidden if the header is missing or incorrect.
    """
    if not header_value or header_value != settings.APP_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Invalid or missing API key."
        )
    return header_value


class ChatRequest(BaseModel):
    """Schema for incoming conversational chat requests."""

    query: str = Field(
        ...,
        max_length=500,
        description="User query text, maximum 500 characters."
    )

    @field_validator("query")
    @classmethod
    def validate_query_not_blank(cls, v: str) -> str:
        """Ensure the query is not empty or consisting exclusively of whitespace.

        Args:
            v: Input query string.

        Returns:
            str: Whitespace-stripped query string.

        Raises:
            ValueError: If input is empty or whitespace-only.
        """
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Query cannot be empty or consist solely of whitespace.")
        return trimmed


@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(
    request: Request,
    body: ChatRequest,
    api_key: str = Depends(get_api_key),
) -> dict[str, Any]:
    """Process a user query against the statutory RAG knowledge base.

    Resolves a thread-safe, request-scoped conversational inference engine,
    executes asynchronous semantic retrieval, and returns response text with
    source citations and performance metadata.

    Args:
        request: FastAPI request context for rate limiting and state access.
        body: Validated ChatRequest payload containing user query.
        api_key: Validated API key from security dependency.

    Returns:
        dict[str, Any]: Structured dictionary with response text, citations, latency,
            estimated token count, and active model metadata.

    Raises:
        HTTPException: 403 for authentication failure, 422 for input validation errors,
            429 for rate limit violations, 503 for service unreadiness, and 500 for
            internal server errors.
    """
    engine: Optional[Any] = None
    vector_index: Optional[Any] = getattr(request.app.state, "vector_index", None)

    if vector_index is not None:
        try:
            from app.engine import get_chat_engine
            engine = get_chat_engine(index=vector_index)
        except Exception as e:
            logger.warning(
                f"Failed to instantiate request-scoped engine ({e}); attempting state fallback."
            )

    if engine is None:
        engine = getattr(request.app.state, "chat_engine", None)

    if engine is None:
        try:
            from app.engine import get_vector_index, get_chat_engine
            request.app.state.vector_index = get_vector_index()
            engine = get_chat_engine(index=request.app.state.vector_index)
            request.app.state.chat_engine = engine
            logger.info("AI Engine and Vector Index loaded successfully on-demand.")
        except Exception as e:
            logger.error(f"Failed to initialize AI Engine on-demand: {e}")
            dispatch_webhook_alert("AI Engine Load Failure", str(e), severity="CRITICAL")
            raise HTTPException(
                status_code=503,
                detail="AI Engine is not ready or failed to connect to the vector database."
            )

    query = body.query
    try:
        start_time = time.time()
        active_provider = settings.LLM_PROVIDER.lower().strip()
        active_model = (
            settings.OLLAMA_MODEL if active_provider == "ollama" else settings.LLM_MODEL
        )
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            f"Query received from {client_ip}: '{query[:50]}...'",
            extra={"extra_data": {"provider": active_provider, "model": active_model}},
        )

        response = await engine.achat(query)

        latency = time.time() - start_time
        answer_text: str = response.response

        total_tokens = estimate_tokens(query, answer_text)
        sources = format_source_citations(response.source_nodes)

        logger.info(
            f"Completed query: latency={latency:.2f}s | tokens=~{total_tokens} | sources={len(sources)}"
        )

        return {
            "response": answer_text,
            "sources": sources,
            "latency": f"{latency:.2f}s",
            "tokens": total_tokens,
            "provider": active_provider,
            "model": active_model,
        }

    except HTTPException:
        raise
    except Exception as e:
        err_msg = str(e) or repr(e)
        logger.error(f"Error during chat query processing: {err_msg}", exc_info=True)

        # Detect local Ollama disconnection
        if any(term in err_msg.lower() for term in ["connection refused", "11434", "failed to connect"]):
            dispatch_webhook_alert(
                "Ollama Connection Refused",
                f"Host: {settings.OLLAMA_BASE_URL}",
                severity="WARNING"
            )
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Connection to Ollama ({settings.OLLAMA_BASE_URL}) failed. "
                    f"Ensure Ollama is running and model '{settings.OLLAMA_MODEL}' is pulled."
                ),
            )

        # Detect cloud rate limits (Groq 429)
        if any(term in err_msg.lower() for term in ["rate_limit", "429", "quota"]):
            dispatch_webhook_alert("Groq API Rate Limit Hit (429)", err_msg, severity="WARNING")
            raise HTTPException(
                status_code=429,
                detail="Cloud AI provider rate limit reached. Please switch to local Ollama mode or wait 1 minute.",
            )

        dispatch_webhook_alert("Unhandled Internal Server Error (500)", err_msg, severity="ERROR")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred while processing your query.",
        )
