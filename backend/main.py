from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import router as api_router
from app.config import settings
from app.utils import check_chroma_heartbeat, limiter
from contextlib import asynccontextmanager
import logging
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Lifespan events (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚙️ Memuat AI Engine dan Koneksi ke Vector DB...")
    try:
        from app.engine import get_chat_engine
        app.state.chat_engine = get_chat_engine()
        logger.info("✅ AI Engine Siap!")
    except Exception as e:
        logger.error(f"❌ Gagal memuat AI Engine: {e}")
        app.state.chat_engine = None
    yield
    logger.info("🛑 Mematikan aplikasi...")

app = FastAPI(title="Legal Chatbot RAG", lifespan=lifespan)

# Register Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

try:
    from llama_index.core import set_global_handler
    set_global_handler("simple")
except ImportError:
    pass

# Include Router
app.include_router(api_router)

# Terapkan Rate Limit di Endpoint Utama
@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {"message": "Legal Chatbot API is running securely!"}

# Endpoint Healthcheck aktif untuk liveness & readiness probe
@app.get("/health")
def health_check(request: Request):
    is_engine_ready = getattr(request.app.state, "chat_engine", None) is not None
    if not is_engine_ready:
        try:
            from app.engine import get_chat_engine
            request.app.state.chat_engine = get_chat_engine()
            is_engine_ready = True
        except Exception:
            is_engine_ready = False

    is_chroma_alive = check_chroma_heartbeat(settings.CHROMA_HOST, settings.CHROMA_PORT)

    all_healthy = is_engine_ready and is_chroma_alive
    status_code = 200 if all_healthy else 503

    payload = {
        "status": "healthy" if all_healthy else "degraded",
        "components": {
            "ai_engine": "ready" if is_engine_ready else "not_ready",
            "chroma_db": "connected" if is_chroma_alive else "unreachable"
        },
        "service": "Legal Chatbot RAG API"
    }

    if not all_healthy:
        return JSONResponse(status_code=status_code, content=payload)
    return payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
