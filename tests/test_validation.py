import pytest
from pydantic import ValidationError
from app.api import ChatRequest


def test_valid_query_accepted():
    """Verify that normal queries (< 500 characters) are accepted and whitespace is trimmed."""
    req = ChatRequest(query="  What is the highway speed limit?  ")
    assert req.query == "What is the highway speed limit?"


def test_blank_whitespace_query_rejected():
    """Verify that queries consisting solely of whitespace are rejected with ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest(query="     ")
    assert "Query cannot be empty" in str(exc_info.value)


def test_empty_query_rejected():
    """Verify that empty string queries are rejected."""
    with pytest.raises(ValidationError):
        ChatRequest(query="")


def test_query_exceeding_500_chars_rejected():
    """Verify that queries exceeding 500 characters violate max_length boundary."""
    long_text = "a" * 501
    with pytest.raises(ValidationError):
        ChatRequest(query=long_text)


def test_endpoint_returns_422_on_invalid_input(test_client):
    """Verify that invalid request bodies return HTTP 422 Unprocessable Entity."""
    headers = {"X-API-Key": "test-secret-key-123"}
    response = test_client.post("/chat", json={"query": "   "}, headers=headers)
    assert response.status_code == 422
