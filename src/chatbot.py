"""Legal Chatbot public facade module."""

from typing import Any, Dict


def get_legal_response(query: str) -> Dict[str, Any]:
    """Public helper to query legal assistant index."""
    return {"query": query, "status": "processed"}
