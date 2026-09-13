def test_missing_api_key_header_returns_403(test_client):
    """Verify that requests missing the X-API-Key header are rejected with HTTP 403."""
    response = test_client.post("/chat", json={"query": "What is SIM A?"})
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_invalid_api_key_header_returns_403(test_client):
    """Verify that requests with an invalid API key are rejected with HTTP 403."""
    headers = {"X-API-Key": "wrong-secret-key"}
    response = test_client.post("/chat", json={"query": "What is SIM A?"}, headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_valid_api_key_header_succeeds(test_client):
    """Verify that requests providing a valid API key header succeed with HTTP 200."""
    headers = {"X-API-Key": "test-secret-key-123"}
    response = test_client.post(
        "/chat", json={"query": "What is the sanction under Article 281?"}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
    assert "tokens" in data
    assert "latency" in data
