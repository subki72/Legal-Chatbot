from fastapi import FastAPI, Request
from app.api import router as api_router
from app.engine import get_chat_engine
from contextlib import asynccontextmanager
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
from llama_index.core import set_global_handler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Lifespan events (Startup & Shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⚙️ Memuat AI Engine dan Koneksi ke Vector DB...")
    try:
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

set_global_handler("simple")

# Include Router
app.include_router(api_router)

# Terapkan Rate Limit di Endpoint Utama
@app.get("/")
@limiter.limit("5/minute")
def root(request: Request):
    return {"message": "Legal Chatbot API is running securely!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
