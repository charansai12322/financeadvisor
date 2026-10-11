"""
Unit tests for DocumentRetrievalService and VectorStoreRepository.
"""
from app.repositories.vector_store import VectorStoreRepository
from app.services.document_retrieval import DocumentRetrievalService


def test_deterministic_chunk_id_generation():
    """Verifies that chunk ID generation is deterministic and unique."""
    id1 = VectorStoreRepository.generate_chunk_id("doc.pdf", page=5, chunk_index=12, content="Text chunk A")
    id2 = VectorStoreRepository.generate_chunk_id("doc.pdf", page=5, chunk_index=12, content="Text chunk A")
    id3 = VectorStoreRepository.generate_chunk_id("doc.pdf", page=5, chunk_index=12, content="Different chunk B")

    assert id1 == id2, "Identical content and indices must produce identical chunk IDs"
    assert id1 != id3, "Different content must produce different chunk IDs"
    assert id1.startswith("doc.pdf_p5_c12_")


def test_agent_tool_context_formatting_when_empty():
    """Verifies format_agent_tool_context provides guidance when no chunks exist."""
    class MockEmptyRepo:
        def search_similarity(self, query: str, top_k: int = 3):
            return []

    service = DocumentRetrievalService(repo=MockEmptyRepo())
    context = service.format_agent_tool_context("Unknown provision")
    assert "No relevant information found" in context
    assert "Do not fabricate" in context
