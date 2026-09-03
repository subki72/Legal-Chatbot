import logging
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from llama_index.core.postprocessor import SentenceTransformerRerank 
import chromadb
from app.config import settings

logger = logging.getLogger(__name__)

def get_chat_engine():
    try:
        # Gunakan HttpClient untuk connect ke server Chroma
        db = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        chroma_collection = db.get_collection("legal_docs")
    except Exception as e:
        logger.error(f"Gagal mengambil collection ChromaDB: {e}")
        raise ValueError(f"ChromaDB error: {e}")
        
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # 2. Embedding Model
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
    
    # 3. Load Index
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    
    # 4. LLM
    llm = Groq(model=settings.LLM_MODEL, api_key=settings.GROQ_API_KEY)

    # 5. Reranker (Opsional - aktif jika USE_RERANKER=True dan model tersedia)
    node_postprocessors = []
    similarity_top_k = 3
    if getattr(settings, "USE_RERANKER", False):
        try:
            reranker = SentenceTransformerRerank(
                model=settings.RERANKER_MODEL, top_n=3
            )
            node_postprocessors.append(reranker)
            similarity_top_k = 10
            logger.info("✅ Re-ranker Model berhasil diaktifkan (top_n=3, similarity_top_k=10).")
        except Exception as e:
            logger.warning(f"⚠️ Re-ranker tidak dapat dimuat ({e}), menggunakan Dense Retrieval top-3.")

    # 6. Chat Engine
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        node_postprocessors=node_postprocessors, 
        similarity_top_k=similarity_top_k, 
        system_prompt=(
            "Anda adalah asisten hukum profesional (AI Legal Assistant). "
            "Jawab pertanyaan pengguna HANYA berdasarkan konteks dokumen UU yang diberikan. "
            "Sebutkan Dasar Hukum (Pasal/Ayat) secara spesifik. "
            "Gunakan Bahasa Indonesia formal. Jika tidak ada di dokumen, katakan tidak tahu."
        )
    )
    
    return chat_engine
