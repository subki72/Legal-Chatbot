import os
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_data():
    logger.info(f"Membaca dokumen dari: {settings.raw_data_dir}")
    
    if not os.path.exists(settings.raw_data_dir) or not os.listdir(settings.raw_data_dir):
        logger.error("Folder Data/raw kosong atau tidak ditemukan!")
        return

    # 2. Load Dokumen PDF
    reader = SimpleDirectoryReader(input_dir=settings.raw_data_dir, recursive=True)
    documents = reader.load_data()
    logger.info(f"Ditemukan {len(documents)} halaman dokumen.")

    # 3. Setup Vector Database (ChromaDB HttpClient)
    try:
        db = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        chroma_collection = db.get_or_create_collection("legal_docs")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
    except Exception as e:
        logger.error(f"Gagal terhubung ke ChromaDB: {e}")
        return

    # 4. Setup Embedding Model
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)

    # 5. Proses Indexing
    logger.info("Sedang memproses (Chunking & Embedding)...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True
    )

    logger.info("Selesai! Data hukum berhasil disimpan ke Vector Database Chroma Server.")

if __name__ == "__main__":
    ingest_data()
