def test_missing_api_key_header_returns_403(test_client):
    """Memverifikasi bahwa request tanpa header X-API-Key ditolak dengan status HTTP 403."""
    response = test_client.post("/chat", json={"query": "Apa itu SIM A?"})
    assert response.status_code == 403
    assert "Akses Ditolak" in response.json()["detail"]

def test_invalid_api_key_header_returns_403(test_client):
    """Memverifikasi bahwa request dengan API key yang salah ditolak dengan status HTTP 403."""
    headers = {"X-API-Key": "wrong-secret-key"}
    response = test_client.post("/chat", json={"query": "Apa itu SIM A?"}, headers=headers)
    assert response.status_code == 403
    assert "Akses Ditolak" in response.json()["detail"]

def test_valid_api_key_header_succeeds(test_client):
    """Memverifikasi bahwa request dengan API key yang benar berhasil diproses (HTTP 200)."""
    headers = {"X-API-Key": "test-secret-key-123"}
    response = test_client.post("/chat", json={"query": "Apa sanksi pasal 281?"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "tokens" in data
    assert "latency" in data
