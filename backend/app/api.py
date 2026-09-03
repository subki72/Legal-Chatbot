from fastapi import APIRouter, HTTPException, Request, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
import time
import logging
from app.config import settings
from app.utils import estimate_tokens, format_source_citations, limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# API Key Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != settings.APP_API_KEY:
        raise HTTPException(status_code=403, detail="Akses Ditolak: API Key tidak valid")
    return api_key_header

class ChatRequest(BaseModel):
    query: str = Field(..., max_length=500, description="Pertanyaan pengguna, maks 500 karakter")

    @field_validator("query")
    @classmethod
    def validate_query_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Pertanyaan tidak boleh kosong atau hanya berisi spasi.")
        return trimmed

@router.post("/chat")
@limiter.limit("5/minute")
async def chat_endpoint(request: Request, body: ChatRequest, api_key: str = Depends(get_api_key)):
    # Ambil engine dari app state (diset saat startup) atau muat on-demand
    chat_engine = getattr(request.app.state, "chat_engine", None)
    if not chat_engine:
        try:
            from app.engine import get_chat_engine
            request.app.state.chat_engine = get_chat_engine()
            chat_engine = request.app.state.chat_engine
            logger.info("✅ AI Engine berhasil dimuat on-demand!")
        except Exception as e:
            logger.error(f"Gagal memuat AI Engine on-demand: {e}")
            raise HTTPException(status_code=503, detail="AI Engine belum siap atau gagal dimuat")

    query = body.query
    try:
        start_time = time.time()
        logger.info(f"🗣️ User IP {request.client.host} bertanya: {query[:50]}...")

        # Gunakan ACHAT (Asynchronous Chat) agar tidak memblokir event loop FastAPI
        response = await chat_engine.achat(query)

        end_time = time.time()
        latency = end_time - start_time
        answer_text = response.response

        # Format token & sitasi via utility helpers
        total_tokens = estimate_tokens(query, answer_text)
        sources = format_source_citations(response.source_nodes)

        logger.info(f"Latency: {latency:.2f}s | Token: ~{total_tokens} | Source: {len(sources)}")

        return {
            "response": answer_text,
            "sources": sources,
            "latency": f"{latency:.2f}s",
            "tokens": total_tokens
        }

    except HTTPException:
        raise
    except Exception as e:
        err_msg = str(e)
        logger.error(f"❌ Error saat memproses chat: {err_msg}")

        # Deteksi khusus jika kuota Groq API / LLM terkena rate limit
        if "rate_limit" in err_msg.lower() or "429" in err_msg or "quota" in err_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Layanan AI sedang mencapai batas kuota (Rate Limit). Silakan tunggu 1 menit sebelum mencoba lagi."
            )

        raise HTTPException(
            status_code=500,
            detail="Terjadi kendala internal server saat memproses pertanyaan Anda."
        )
