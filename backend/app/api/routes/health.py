"""
Health check endpoints.
"""
from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Lightweight process health check")
async def health_check():
    """
    Lightweight health check endpoint.
    Guarantees zero secret leakage and does not depend on external model availability.
    """
    return HealthResponse(status="ok", service="finance-advisor")
