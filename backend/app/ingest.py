import glob
import logging
import os
from typing import Optional
import chromadb
from llama_index.core import Document, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import pypdf
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_documents_from_dir(data_dir: str) -> list[Document]:
    """Extract and parse document pages from the raw data directory.

    Parses PDF documents on a per-page basis using pypdf to ensure high-fidelity text
    extraction and exact page metadata attribution. Also ingests plain text or markdown
    files if present.

    Args:
        data_dir: Directory path containing source documents.

    Returns:
        list[Document]: Extracted LlamaIndex Document instances with metadata.
    """
    if not os.path.exists(data_dir):
        logger.error(f"Target directory does not exist: {data_dir}")
        return []

    documents: list[Document] = []

    # 1. Parse PDF documents page-by-page
    pdf_files = glob.glob(os.path.join(data_dir, "**", "*.pdf"), recursive=True)
    for pdf_path in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf_path)
            file_name = os.path.basename(pdf_path)
            logger.info(f"Extracting PDF '{file_name}' ({len(reader.pages)} pages)...")
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    doc = Document(
                        text=text,
                        metadata={
                            "file_name": file_name,
                            "file_path": pdf_path,
                            "page_label": str(page_idx + 1),
                        },
                    )
                    documents.append(doc)
        except Exception as e:
            logger.error(f"Failed to read PDF document at {pdf_path}: {e}")

    # 2. Parse supplementary non-PDF files (e.g. .txt, .md)
    non_pdf_files = [
        f
        for f in glob.glob(os.path.join(data_dir, "**", "*.*"), recursive=True)
        if not f.lower().endswith(".pdf")
    ]
    if non_pdf_files:
        try:
            dir_reader = SimpleDirectoryReader(input_files=non_pdf_files)
            documents.extend(dir_reader.load_data())
        except Exception as e:
            logger.warning(f"Notice while parsing non-PDF files: {e}")

    return documents


def ingest_data() -> None:
    """Execute complete ingestion pipeline: load, chunk, embed, and store in ChromaDB.

    Cleans prior collection, configures SentenceSplitter chunking, and persists
    dense vectors into the ChromaDB service.
    """
    logger.info(f"Reading source documents from: {settings.raw_data_dir}")

    if not os.path.exists(settings.raw_data_dir) or not os.listdir(settings.raw_data_dir):
        logger.error("Raw data directory is missing or empty. Ingestion aborted.")
        return

    # 1. Extract documents with text parsing
    documents = load_documents_from_dir(settings.raw_data_dir)
    logger.info(f"Extracted {len(documents)} valid text document pages.")

    if not documents:
        logger.warning("No readable text documents discovered. Aborting vector indexing.")
        return

    # 2. Setup Vector Database (ChromaDB HttpClient)
    try:
        db = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        try:
            db.delete_collection("legal_docs")
            logger.info("Prior collection 'legal_docs' purged for clean re-indexing.")
        except Exception:
            pass

        chroma_collection = db.get_or_create_collection("legal_docs")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        return

    # 3. Setup Embedding Model & Text Splitter
    cache_dir: Optional[str] = None
    for candidate in [
        "/home/appuser/.cache/huggingface/hub",
        os.path.expanduser("~/.cache/huggingface/hub"),
    ]:
        if os.path.exists(os.path.dirname(candidate)):
            cache_dir = candidate
            break

    embed_model = HuggingFaceEmbedding(
        model_name=settings.EMBEDDING_MODEL,
        cache_folder=cache_dir,
    )
    transformations = [SentenceSplitter(chunk_size=1024, chunk_overlap=128)]

    # 4. Execute Vector Indexing
    logger.info("Processing chunking and embedding generation for statutory documents...")
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=transformations,
        show_progress=True,
    )

    logger.info("Completed! High-quality legal embeddings persisted to ChromaDB collection.")


if __name__ == "__main__":
    ingest_data()
