import logging
from typing import List, Any
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Shared Rate Limiter Instance
limiter = Limiter(key_func=get_remote_address)

def estimate_tokens(query: str, answer_text: str) -> int:
    """
    Menghitung perkiraan kasar total token (input + output) berdasarkan word count.
    Rasio 1.3 kata/token umum digunakan untuk estimasi cepat tanpa overhead tokenizer.
    """
    input_tokens = len(query.split()) * 1.3
    output_tokens = len(answer_text.split()) * 1.3
    return int(input_tokens + output_tokens)

def format_source_citations(source_nodes: List[Any]) -> List[str]:
    """
    Mengekstrak informasi file dan nomor halaman dari metadata source nodes LlamaIndex.
    Mengembalikan daftar referensi dokumen unik yang telah disortir.
    """
    sources = []
    for node in source_nodes:
        meta = getattr(node, "metadata", None)
        if meta is None and hasattr(node, "node"):
            meta = getattr(node.node, "metadata", {})
        if not meta:
            meta = {}

        file_name = meta.get("file_name", "Dokumen")
        page = meta.get("page_label", "?")
        sources.append(f"{file_name} (Hal. {page})")

    return sorted(list(set(sources)))

def check_chroma_heartbeat(host: str, port: int) -> bool:
    """
    Memeriksa ketersediaan server ChromaDB via HttpClient heartbeat.
    """
    try:
        import chromadb
        client = chromadb.HttpClient(host=host, port=port)
        heartbeat = client.heartbeat()
        return heartbeat is not None and heartbeat > 0
    except Exception as e:
        logger.warning(f"Koneksi ChromaDB heartbeat gagal: {e}")
        return False
