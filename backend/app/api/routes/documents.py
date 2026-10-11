"""
Document search and status endpoints.
"""
from fastapi import APIRouter
from app.schemas.documents import (
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentStatusResponse,
)
from app.services.document_retrieval import document_retrieval_service

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.post("/search", response_model=DocumentSearchResponse, summary="Search GST and financial documents")
async def search_documents(request: DocumentSearchRequest):
    """
    Retrieves grounded evidence chunks from official SEBI and CBIC reference PDFs.
    Returns filenames and verified page numbers.
    """
    return document_retrieval_service.search_documents(
        question=request.question,
        top_k=request.top_k,
    )


@router.get("/status", response_model=DocumentStatusResponse, summary="Get document index status")
async def get_document_status():
    """Returns indexing and document count diagnostics without leaking internal paths or secrets."""
    return document_retrieval_service.get_status()
