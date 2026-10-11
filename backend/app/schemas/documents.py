"""
Document retrieval schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A retrieved text chunk with source provenance and safe page metadata."""
    content: str = Field(description="Extracted chunk text content")
    source: str = Field(description="Originating document filename")
    page: Optional[int] = Field(default=None, description="0-indexed source page number if known")
    page_label: str = Field(description="Safe display label e.g. 'Page 6' or 'Page Unknown'")
    score: Optional[float] = Field(default=None, description="Vector similarity / distance score if provided")


class DocumentSearchRequest(BaseModel):
    """Search request payload for querying the knowledge base."""
    question: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Query text regarding GST, tax rules, or financial education",
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve (1 to 10)",
    )


class DocumentSearchResponse(BaseModel):
    """Search response payload containing retrieved document evidence."""
    question: str = Field(description="Echo of query question")
    total_results: int = Field(description="Number of chunks retrieved")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="Retrieved chunks")


class DocumentStatusResponse(BaseModel):
    """Diagnostic status of document ingestion and vector database."""
    indexed: bool = Field(description="True if vector index exists and has chunks")
    collection_name: str = Field(description="Active Chroma collection name")
    total_chunks: int = Field(description="Total chunks currently stored in vector collection")
    available_documents: List[str] = Field(
        default_factory=list,
        description="Names of reference documents in the knowledge base",
    )
