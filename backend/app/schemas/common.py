"""
Common shared Pydantic response models.
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized error envelope returned by all error handlers."""
    error: str = Field(description="High-level error description or category")
    status_code: int = Field(description="HTTP status code")
    message: str = Field(description="Detailed error explanation")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic details")
    request_id: Optional[str] = Field(default=None, description="Request tracking identifier")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Process health status")
    service: str = Field(default="finance-advisor", description="Service identifier")
