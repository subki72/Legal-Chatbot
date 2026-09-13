import logging
import urllib.request
from typing import Any
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

# Shared Rate Limiter Instance
limiter = Limiter(key_func=get_remote_address)


def estimate_tokens(query: str, answer_text: str) -> int:
    """Estimate total tokens (prompt + completion) based on word count.

    Applies a standard empirical ratio of 1.3 tokens per whitespace-delimited word
    to provide lightweight estimation without tokenizer overhead.

    Args:
        query: Input user query string.
        answer_text: Generated assistant response string.

    Returns:
        int: Estimated total token count.
    """
    if not query and not answer_text:
        return 0

    input_tokens = len(query.split()) * 1.3
    output_tokens = len(answer_text.split()) * 1.3
    return int(input_tokens + output_tokens)


def format_source_citations(source_nodes: list[Any]) -> list[str]:
    """Extract and deduplicate document citations from LlamaIndex source nodes.

    Extracts file names and page labels from node metadata, formats them consistently,
    and returns a sorted list of unique citations.

    Args:
        source_nodes: List of retrieval source node objects.

    Returns:
        list[str]: Sorted list of unique formatted citation strings (e.g., 'Doc.pdf (Page 12)').
    """
    if not source_nodes:
        return []

    sources: list[str] = []
    for node in source_nodes:
        meta: dict[str, Any] = getattr(node, "metadata", None)
        if meta is None and hasattr(node, "node"):
            meta = getattr(node.node, "metadata", {})
        if not meta:
            meta = {}

        file_name = meta.get("file_name", "Document")
        page = meta.get("page_label", "?")
        sources.append(f"{file_name} (Page {page})")

    return sorted(list(set(sources)))


def check_chroma_heartbeat(host: str, port: int) -> bool:
    """Verify ChromaDB connectivity via direct HTTP heartbeat or client ping.

    Attempts a lightweight HTTP GET request to /api/v1/heartbeat, falling back
    to chromadb.HttpClient if the direct socket connection encounters an error.

    Args:
        host: ChromaDB hostname or IP address.
        port: ChromaDB network port.

    Returns:
        bool: True if ChromaDB responds with a healthy heartbeat, False otherwise.
    """
    if not host or port <= 0:
        return False

    try:
        url = f"http://{host}:{port}/api/v1/heartbeat"
        req = urllib.request.Request(url, headers={"User-Agent": "HealthProbe/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        try:
            import chromadb
            client = chromadb.HttpClient(host=host, port=port)
            heartbeat = client.heartbeat()
            return heartbeat is not None and heartbeat > 0
        except Exception as e:
            logger.warning(f"ChromaDB heartbeat probe failed for {host}:{port}: {e}")
            return False
