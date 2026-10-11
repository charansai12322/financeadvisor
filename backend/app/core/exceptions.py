"""
Custom application domain exceptions.
"""
from typing import Any, Dict, Optional


class FinanceAdvisorException(Exception):
    """Base exception for all domain-level errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class MarketDataUnavailableException(FinanceAdvisorException):
    """Raised when upstream Gold-API is unreachable, times out, or returns a 5xx error."""
    def __init__(self, message: str = "Upstream market data service is unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=502, details=details)


class UnsupportedAssetException(FinanceAdvisorException):
    """Raised when an unsupported commodity asset symbol is requested."""
    def __init__(self, asset: str, supported: list = None):
        supported_str = ", ".join(supported or ["gold", "silver"])
        super().__init__(
            message=f"Unsupported asset '{asset}'. Supported assets: {supported_str}",
            status_code=400,
            details={"asset": asset, "supported_assets": supported or ["gold", "silver"]},
        )


class GeminiUnconfiguredException(FinanceAdvisorException):
    """Raised when Gemini-powered agent is invoked without an API key configured."""
    def __init__(self, message: str = "Gemini API key is not configured. Please set GEMINI_API_KEY in .env."):
        super().__init__(message=message, status_code=503)


class GeminiInferenceException(FinanceAdvisorException):
    """Raised when Gemini API call fails (quota exhausted, invalid key, model timeout)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=502, details=details)


class GeminiRateLimitException(FinanceAdvisorException):
    """Raised when Gemini API rate limit is reached (HTTP 429)."""
    def __init__(self, message: str = "Gemini API rate limit exceeded. Please wait a moment before trying again.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=429, details=details)


class GeminiQuotaExceededException(FinanceAdvisorException):
    """Raised when Gemini API quota is exhausted (HTTP 429)."""
    def __init__(self, message: str = "Gemini API quota has been exhausted. Please verify project quota or billing in Google AI Studio.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=429, details=details)


class DocumentRetrievalException(FinanceAdvisorException):
    """Raised when vector similarity search or document loading fails."""
    def __init__(self, message: str = "Failed to retrieve documents from vector knowledge base", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)


class DocumentIngestionException(FinanceAdvisorException):
    """Raised when PDF ingestion fails."""
    def __init__(self, message: str = "Failed to ingest reference PDF documents", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
