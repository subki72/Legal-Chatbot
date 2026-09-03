def test_root_endpoint(test_client):
    """Memverifikasi bahwa endpoint root / mengembalikan status 200 dan pesan sambutan."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Legal Chatbot API" in data["message"]

def test_health_endpoint_structure(test_client):
    """Memverifikasi bahwa endpoint /health mengembalikan format payload JSON yang standar."""
    response = test_client.get("/health")
    # Status code bisa 200 (jika chroma aktif) atau 503 (jika chroma offline di dev)
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "ai_engine" in data["components"]
    assert "chroma_db" in data["components"]
    assert "service" in data
    assert data["service"] == "Legal Chatbot RAG API"
