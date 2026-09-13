from unittest.mock import MagicMock
from app.utils import check_chroma_heartbeat, estimate_tokens, format_source_citations


def test_estimate_tokens_normal():
    """Test token estimation on standard query and response text."""
    query = "What is the penalty for Article 281?"
    answer = "The sanction is imprisonment for up to 4 months."
    tokens = estimate_tokens(query, answer)
    # query: 7 words * 1.3 = 9.1; answer: 9 words * 1.3 = 11.7; total: int(20.8) = 20
    assert tokens > 0
    assert tokens == 20


def test_estimate_tokens_empty():
    """Test token estimation when inputs are empty strings."""
    tokens = estimate_tokens("", "")
    assert tokens == 0


def test_format_source_citations_with_duplicates():
    """Test that format_source_citations deduplicates and sorts references alphabetically."""

    class MockNode:
        def __init__(self, file_name, page_label):
            self.metadata = {"file_name": file_name, "page_label": page_label}

    class MockSource:
        def __init__(self, file_name, page):
            self.node = MockNode(file_name, page)

    source_nodes = [
        MockSource("UU Nomor 22 Tahun 2009.pdf", "15"),
        MockSource("UU Nomor 22 Tahun 2009.pdf", "15"),  # duplicate
        MockSource("UU Nomor 22 Tahun 2009.pdf", "88"),
        MockSource("Other_Statute.pdf", "1"),
    ]

    citations = format_source_citations(source_nodes)

    assert len(citations) == 3
    assert "UU Nomor 22 Tahun 2009.pdf (Page 15)" in citations
    assert "UU Nomor 22 Tahun 2009.pdf (Page 88)" in citations
    assert "Other_Statute.pdf (Page 1)" in citations
    assert citations == sorted(citations)


def test_format_source_citations_empty():
    """Test format_source_citations when input list is empty."""
    citations = format_source_citations([])
    assert citations == []


def test_check_chroma_heartbeat_offline():
    """Verify that heartbeat probe returns False safely when target service is unreachable."""
    is_alive = check_chroma_heartbeat(host="127.0.0.1", port=59999)
    assert is_alive is False
