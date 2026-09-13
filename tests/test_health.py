def test_root_endpoint(test_client):
    """Verify that the root endpoint returns HTTP 200 and operational greeting message."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Legal Chatbot API" in data["message"]


def test_health_endpoint_structure(test_client):
    """Verify that the /health endpoint returns standard health payload schema."""
    response = test_client.get("/health")
    # Status code can be 200 (if chroma is reachable) or 503 (if chroma offline in dev)
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "ai_engine" in data["components"]
    assert "chroma_db" in data["components"]
    assert "service" in data
    assert data["service"] == "Legal Chatbot RAG API"
