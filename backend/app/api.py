from fastapi import APIRouter, HTTPException, Request, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
import time 
import logging
from app.config import settings

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

@router.post("/chat")
async def chat_endpoint(request: Request, body: ChatRequest, api_key: str = Depends(get_api_key)):
    # Ambil engine dari app state (diset saat startup)
    chat_engine = request.app.state.chat_engine
    if not chat_engine:
         raise HTTPException(status_code=503, detail="AI Engine belum siap")

    # Terapkan rate limit pada endpoint chat secara manual karena berada dalam APIRouter
    limiter = request.app.state.limiter
    try:
        limiter.check_request_limit(request, "5/minute", "", "")
    except Exception as e:
        raise e

    query = body.query
    try:
        start_time = time.time()
        logger.info(f"🗣️ User IP {request.client.host} bertanya: {query[:50]}...")
        
        # 2. Gunakan ACHAT (Asynchronous Chat) agar tidak memblokir FastAPI
        response = await chat_engine.achat(query)
        
        end_time = time.time()
        latency = end_time - start_time
        
        # 4. Hitung Token (Estimasi Kasar)
        input_tokens = len(query.split()) * 1.3
        output_tokens = len(response.response.split()) * 1.3
        total_tokens = int(input_tokens + output_tokens)
        
        logger.info(f"Latency: {latency:.2f}s | Token: ~{total_tokens} | Source: {len(response.source_nodes)}")
        
        # --- Proses Data untuk Frontend ---
        answer_text = response.response
        sources = []
        for node in response.source_nodes:
            meta = node.node.metadata
            file_name = meta.get('file_name', 'Dokumen')
            page = meta.get('page_label', '?')
            sources.append(f"{file_name} (Hal. {page})")
        
        sources = list(set(sources))
            
        return {
            "response": answer_text,
            "sources": sources,
            "latency": f"{latency:.2f}s",
            "tokens": total_tokens
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error saat memproses chat: {e}")
        # Jangan expose real error traceback ke luar!
        raise HTTPException(status_code=500, detail="Terjadi kendala internal server saat memproses pertanyaan Anda.")
