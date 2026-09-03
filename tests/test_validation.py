import pytest
from pydantic import ValidationError
from app.api import ChatRequest

def test_valid_query_accepted():
    """Memverifikasi bahwa query normal (< 500 karakter) valid dan whitespace-nya di-trim."""
    req = ChatRequest(query="  Berapa batas kecepatan di jalan tol?  ")
    assert req.query == "Berapa batas kecepatan di jalan tol?"

def test_blank_whitespace_query_rejected():
    """Memverifikasi bahwa query yang hanya berisi spasi ditolak dengan ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ChatRequest(query="     ")
    assert "tidak boleh kosong atau hanya berisi spasi" in str(exc_info.value)

def test_empty_query_rejected():
    """Memverifikasi bahwa query kosong ditolak."""
    with pytest.raises(ValidationError):
        ChatRequest(query="")

def test_query_exceeding_500_chars_rejected():
    """Memverifikasi bahwa query melebihi 500 karakter ditolak oleh batas max_length."""
    long_text = "a" * 501
    with pytest.raises(ValidationError):
        ChatRequest(query=long_text)

def test_endpoint_returns_422_on_invalid_input(test_client):
    """Memverifikasi bahwa request dengan body invalid mengembalikan HTTP 422 Unprocessable Entity."""
    headers = {"X-API-Key": "test-secret-key-123"}
    response = test_client.post("/chat", json={"query": "   "}, headers=headers)
    assert response.status_code == 422
