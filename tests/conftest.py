import os
import sys
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"
)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set test environment variables before module imports
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "qwen2.5:7b"
os.environ["APP_API_KEY"] = "test-secret-key-123"
os.environ["GROQ_API_KEY"] = "test-groq-key-456"
os.environ["CHROMA_HOST"] = "localhost"
os.environ["CHROMA_PORT"] = "8000"


@pytest.fixture
def test_client():
    """Provide a configured FastAPI TestClient with a mock chat_engine in app.state.

    Prevents test suites from requiring live external connections to ChromaDB or Ollama/Groq.
    """
    from main import app

    # Configure mock chat engine
    mock_engine = MagicMock()
    mock_response = MagicMock()
    mock_response.response = (
        "Pursuant to Article 281 of Law No. 22 of 2009, the sanction is confinement."
    )

    mock_node = MagicMock()
    mock_node.metadata = {"file_name": "UU Nomor 22 Tahun 2009.pdf", "page_label": "88"}
    mock_response.source_nodes = [mock_node]

    async def mock_achat(query: str):
        return mock_response

    mock_engine.achat = mock_achat
    app.state.chat_engine = mock_engine
    app.state.vector_index = None

    with TestClient(app) as client:
        # Re-attach mock engine post-lifespan initialization
        client.app.state.vector_index = None
        client.app.state.chat_engine = mock_engine
        yield client
