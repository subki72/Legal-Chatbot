import os
import sys
import pytest
from unittest.mock import MagicMock

# Pastikan folder backend ada di sys.path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set environment variables pengujian sebelum modul diimpor
os.environ["APP_API_KEY"] = "test-secret-key-123"
os.environ["GROQ_API_KEY"] = "test-groq-key-456"
os.environ["CHROMA_HOST"] = "localhost"
os.environ["CHROMA_PORT"] = "8000"

from fastapi.testclient import TestClient

@pytest.fixture
def test_client():
    """
    Menyediakan TestClient FastAPI dengan mock chat_engine di app.state
    agar pengujian endpoint tidak memerlukan koneksi server ChromaDB atau Groq riil.
    """
    from main import app

    # Mock chat engine di app.state
    mock_engine = MagicMock()
    mock_response = MagicMock()
    mock_response.response = "Berdasarkan Pasal 281 UU No. 22 Tahun 2009, sanksinya adalah pidana kurungan."

    mock_node = MagicMock()
    mock_node.metadata = {"file_name": "UU Nomor 22 Tahun 2009.pdf", "page_label": "88"}
    mock_response.source_nodes = [mock_node]

    async def mock_achat(query):
        return mock_response

    mock_engine.achat = mock_achat
    app.state.chat_engine = mock_engine

    with TestClient(app) as client:
        # Set mock engine setelah lifespan startup selesai
        client.app.state.chat_engine = mock_engine
        yield client
