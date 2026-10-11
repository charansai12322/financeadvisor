"""
Document Retrieval Service.
Provides high-level knowledge base search and agent context formatting.
"""
from typing import List, Optional
from app.core.exceptions import DocumentRetrievalException
from app.core.logging import logger
from app.repositories.vector_store import (
    VectorStoreRepository,
    vector_store_repository,
)
from app.schemas.documents import (
    DocumentChunk,
    DocumentSearchResponse,
    DocumentStatusResponse,
)


class DocumentRetrievalService:
    """Service providing search across financial and GST reference documents."""

    def __init__(self, repo: Optional[VectorStoreRepository] = None):
        self.repo = repo or vector_store_repository

    def search_documents(self, question: str, top_k: int = 3) -> DocumentSearchResponse:
        """
        Retrieves top_k relevant chunks from the vector database for a user query.
        Guarantees safe page labels and clean source metadata.
        """
        clamped_k = max(1, min(10, top_k))
        try:
            chunks = self.repo.search_similarity(query=question, top_k=clamped_k)
            return DocumentSearchResponse(
                question=question,
                total_results=len(chunks),
                chunks=chunks,
            )
        except Exception as e:
            logger.error(f"Document retrieval error for query '{question[:50]}...': {e}")
            raise DocumentRetrievalException(
                message=f"Error executing vector retrieval: {str(e)}",
                details={"query": question, "error": str(e)},
            )

    def get_status(self) -> DocumentStatusResponse:
        """Returns current indexing status and document counts."""
        status = self.repo.get_status()
        return DocumentStatusResponse(
            indexed=status["indexed"],
            collection_name=status["collection_name"],
            total_chunks=status["total_chunks"],
            available_documents=status["available_documents"],
        )

    def format_agent_tool_context(self, question: str, top_k: int = 3) -> str:
        """
        Formats search results into a clean text block for the LLM agent tool.
        Replaces vulnerable Cell 8 logic with defensive metadata formatting.
        """
        try:
            res = self.search_documents(question=question, top_k=top_k)
            if not res.chunks:
                return (
                    "No relevant information found in the supplied official financial documents. "
                    "Do not fabricate tax rules or financial provisions."
                )

            blocks = []
            for chunk in res.chunks:
                block = f"Source: {chunk.source} ({chunk.page_label})\nContent: {chunk.content}"
                blocks.append(block)

            return "\n\n".join(blocks)
        except Exception as e:
            logger.error(f"Tool context retrieval failed: {e}")
            return f"Notice: Document retrieval encountered a temporary error: {str(e)}"


# Singleton service instance
document_retrieval_service = DocumentRetrievalService()
