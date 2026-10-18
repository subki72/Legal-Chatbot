from unittest.mock import MagicMock, patch
import pytest


def test_root_endpoint_includes_provider_info(test_client):
    """Verify that the root endpoint returns active provider and model metadata."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data
    assert data["status"] == "ready"


def test_health_endpoint_includes_provider_info(test_client):
    """Verify that the health check endpoint returns active provider and model metadata."""
    response = test_client.get("/health")
    data = response.json()
    assert "provider" in data
    assert "model" in data


def test_chat_response_includes_provider_metadata(test_client):
    """Verify that chat responses include provider and model telemetry metadata."""
    headers = {"X-API-Key": "test-secret-key-123"}
    response = test_client.post(
        "/chat", json={"query": "What is the sanction under Article 281?"}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data
    assert data["provider"] in ["ollama", "groq"]


def test_get_llm_factory_ollama():
    """Test get_llm factory instantiation when LLM_PROVIDER=ollama."""
    from app.engine import get_llm

    mock_ollama_cls = MagicMock()
    mock_module = MagicMock()
    mock_module.Ollama = mock_ollama_cls

    with patch("app.config.settings.LLM_PROVIDER", "ollama"), patch(
        "app.config.settings.OLLAMA_MODEL", "qwen2.5:7b"
    ), patch(
        "app.config.settings.OLLAMA_BASE_URL", "http://localhost:11434"
    ), patch(
        "app.config.settings.OLLAMA_TIMEOUT", 60.0
    ), patch.dict(
        "sys.modules", {"llama_index.llms.ollama": mock_module}
    ):
        llm = get_llm()
        assert llm is not None
        mock_ollama_cls.assert_called_once_with(
            model="qwen2.5:7b",
            base_url="http://localhost:11434",
            request_timeout=60.0,
        )


def test_get_llm_factory_groq():
    """Test get_llm factory instantiation when LLM_PROVIDER=groq."""
    from app.engine import get_llm

    mock_groq_cls = MagicMock()
    mock_module = MagicMock()
    mock_module.Groq = mock_groq_cls

    dummy_key = "dummy_mock_groq_key"
    with patch("app.config.settings.LLM_PROVIDER", "groq"), patch(
        "app.config.settings.LLM_MODEL", "llama-3.3-70b-versatile"
    ), patch("app.config.settings.GROQ_API_KEY", dummy_key), patch.dict(
        "sys.modules", {"llama_index.llms.groq": mock_module}
    ):
        llm = get_llm()
        assert llm is not None
        mock_groq_cls.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            api_key=dummy_key,
        )


def test_get_llm_factory_groq_missing_key():
    """Verify that get_llm rejects missing GROQ_API_KEY in groq mode."""
    from app.engine import get_llm

    with patch("app.config.settings.LLM_PROVIDER", "groq"), patch(
        "app.config.settings.GROQ_API_KEY", None
    ):
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        assert "GROQ_API_KEY is required" in str(exc_info.value)


def test_get_llm_factory_unsupported_provider():
    """Verify that get_llm rejects unsupported provider configurations."""
    from app.engine import get_llm

    with patch("app.config.settings.LLM_PROVIDER", "unsupported_llm"):
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        assert "not recognized" in str(exc_info.value)
