from unittest.mock import MagicMock
from app.utils import estimate_tokens, format_source_citations, check_chroma_heartbeat

def test_estimate_tokens_normal():
    """Menguji estimasi token pada query dan jawaban normal."""
    query = "Apa sanksi pasal 281?"
    answer = "Sanksinya pidana kurungan paling lama 4 bulan."
    tokens = estimate_tokens(query, answer)
    # query: 4 kata * 1.3 = 5.2; answer: 7 kata * 1.3 = 9.1; total: int(14.3) = 14
    assert tokens > 0
    assert tokens == 14

def test_estimate_tokens_empty():
    """Menguji estimasi token jika input kosong."""
    tokens = estimate_tokens("", "")
    assert tokens == 0

def test_format_source_citations_with_duplicates():
    """Menguji bahwa format_source_citations melakukan deduplikasi dan sorting dengan benar."""
    class MockNode:
        def __init__(self, file_name, page_label):
            self.metadata = {"file_name": file_name, "page_label": page_label}

    class MockSource:
        def __init__(self, file_name, page):
            self.node = MockNode(file_name, page)

    source_nodes = [
        MockSource("UU Nomor 22 Tahun 2009.pdf", "15"),
        MockSource("UU Nomor 22 Tahun 2009.pdf", "15"),  # duplikat
        MockSource("UU Nomor 22 Tahun 2009.pdf", "88"),
        MockSource("UU Lain.pdf", "1")
    ]

    citations = format_source_citations(source_nodes)

    assert len(citations) == 3
    assert "UU Nomor 22 Tahun 2009.pdf (Hal. 15)" in citations
    assert "UU Nomor 22 Tahun 2009.pdf (Hal. 88)" in citations
    assert "UU Lain.pdf (Hal. 1)" in citations
    # Verifikasi pengurutan alfabetis
    assert citations == sorted(citations)

def test_format_source_citations_empty():
    """Menguji format_source_citations pada list kosong."""
    citations = format_source_citations([])
    assert citations == []

def test_check_chroma_heartbeat_offline():
    """Menguji bahwa pengecekan heartbeat ke host/port mati mengembalikan False secara aman."""
    is_alive = check_chroma_heartbeat(host="127.0.0.1", port=59999)
    assert is_alive is False
