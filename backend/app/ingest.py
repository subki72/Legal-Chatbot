import os
import glob
import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
import pypdf
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_documents_from_dir(data_dir: str):
    """
    Membaca dan mem-parsing dokumen PDF dengan pypdf secara presisi per halaman.
    Menghindari bug SimpleDirectoryReader yang membaca PDF sebagai raw binary bytes.
    """
    documents = []
    
    # 1. Parsing dokumen PDF
    pdf_files = glob.glob(os.path.join(data_dir, "**", "*.pdf"), recursive=True)
    for pdf_path in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf_path)
            file_name = os.path.basename(pdf_path)
            logger.info(f"📖 Mengekstrak PDF '{file_name}' ({len(reader.pages)} halaman)...")
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    doc = Document(
                        text=text,
                        metadata={
                            "file_name": file_name,
                            "file_path": pdf_path,
                            "page_label": str(page_idx + 1),
                        }
                    )
                    documents.append(doc)
        except Exception as e:
            logger.error(f"Gagal membaca PDF {pdf_path}: {e}")

    # 2. Parsing file non-PDF jika ada (misal .txt atau .md)
    non_pdf_files = [
        f for f in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True)
        if not f.lower().endswith(".pdf")
    ]
    if non_pdf_files:
        try:
            dir_reader = SimpleDirectoryReader(input_files=non_pdf_files)
            documents.extend(dir_reader.load_data())
        except Exception as e:
            logger.warning(f"Catatan membaca file non-PDF: {e}")

    return documents

def ingest_data():
    logger.info(f"Membaca dokumen dari: {settings.raw_data_dir}")
    
    if not os.path.exists(settings.raw_data_dir) or not os.listdir(settings.raw_data_dir):
        logger.error("Folder Data/raw kosong atau tidak ditemukan!")
        return

    # 1. Ekstrak Dokumen dengan Parsing Teks Nyata
    documents = load_documents_from_dir(settings.raw_data_dir)
    logger.info(f"Ditemukan {len(documents)} halaman dokumen teks valid.")

    # 2. Setup Vector Database (ChromaDB HttpClient)
    try:
        db = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        # Bersihkan koleksi lama jika ada data biner rusak
        try:
            db.delete_collection("legal_docs")
            logger.info("🗑️ Koleksi lama 'legal_docs' dibersihkan untuk re-indexing bersih.")
        except Exception:
            pass
        
        chroma_collection = db.get_or_create_collection("legal_docs")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
    except Exception as e:
        logger.error(f"Gagal terhubung ke ChromaDB: {e}")
        return

    # 3. Setup Embedding Model & Text Splitter
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
    transformations = [SentenceSplitter(chunk_size=1024, chunk_overlap=128)]

    # 4. Proses Indexing
    logger.info("Sedang memproses (Chunking & Embedding teks hukum)...")
    VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=transformations,
        show_progress=True
    )

    logger.info("✅ Selesai! Data hukum berkualitas tinggi berhasil disimpan ke Vector Database Chroma Server.")

if __name__ == "__main__":
    ingest_data()
