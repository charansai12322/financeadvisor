"""
API Contract Tests for all FastAPI endpoints using TestClient.
Verifies HTTP status codes, request validation, headers, and response schemas.
"""
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.core.exceptions import (
    GeminiQuotaExceededException,
    GeminiRateLimitException,
)
from app.main import app
from app.schemas.advisor import AdvisorResponse
from app.schemas.prices import PriceMetadata, PriceResponse

client = TestClient(app)


def test_health_endpoint_contract():
    """Verifies GET /health contract."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "finance-advisor"
    assert "X-Request-ID" in response.headers


def test_prices_gold_endpoint_contract():
    """Verifies GET /api/v1/prices/gold contract."""
    mock_price = PriceResponse(
        asset="Gold",
        symbol="XAU",
        currency="INR",
        currency_symbol="₹",
        price_per_troy_ounce=406258.70,
        price_per_gram=13061.51,
        price_per_10g=130615.11,
        price_per_kg=13061511.0,
        formatted="Gold: ₹13061.51 per gram",
        metadata=PriceMetadata(
            source="Gold-API",
            source_updated_at="2026-10-11T14:00:00Z",
            source_updated_at_readable="just now",
            retrieved_at="2026-10-11T14:05:00Z",
        ),
    )

    with patch("app.services.market_data.market_data_service.get_spot_price", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_price
        response = client.get("/api/v1/prices/gold")
        assert response.status_code == 200
        data = response.json()
        assert data["asset"] == "Gold"
        assert data["symbol"] == "XAU"
        assert data["price_per_gram"] == 13061.51
        assert data["metadata"]["source"] == "Gold-API"
        assert "X-Request-ID" in response.headers


def test_prices_silver_endpoint_contract():
    """Verifies GET /api/v1/prices/silver contract."""
    mock_price = PriceResponse(
        asset="Silver",
        symbol="XAG",
        currency="INR",
        currency_symbol="₹",
        price_per_troy_ounce=5900.00,
        price_per_gram=189.69,
        price_per_10g=1896.90,
        price_per_kg=189690.0,
        formatted="Silver: ₹189.69 per gram",
        metadata=PriceMetadata(
            source="Gold-API",
            retrieved_at="2026-10-11T14:05:00Z",
        ),
    )

    with patch("app.services.market_data.market_data_service.get_spot_price", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_price
        response = client.get("/api/v1/prices/silver")
        assert response.status_code == 200
        data = response.json()
        assert data["asset"] == "Silver"
        assert data["symbol"] == "XAG"


def test_prices_unsupported_asset_returns_400():
    """Verifies GET /api/v1/prices/{unsupported} returns HTTP 400 with structured error."""
    response = client.get("/api/v1/prices/copper")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "UnsupportedAssetException"
    assert "Unsupported asset 'copper'" in data["message"]


def test_documents_status_endpoint_contract():
    """Verifies GET /api/v1/documents/status contract."""
    response = client.get("/api/v1/documents/status")
    assert response.status_code == 200
    data = response.json()
    assert "indexed" in data
    assert "collection_name" in data
    assert "total_chunks" in data


def test_documents_search_endpoint_contract():
    """Verifies POST /api/v1/documents/search contract."""
    payload = {"question": "What is the GST rate on gold?", "top_k": 2}
    response = client.post("/api/v1/documents/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == payload["question"]
    assert "total_results" in data
    assert "chunks" in data
    assert isinstance(data["chunks"], list)


def test_documents_search_invalid_top_k_returns_422():
    """Verifies POST /api/v1/documents/search with top_k > 10 returns 422 validation error."""
    payload = {"question": "What is GST?", "top_k": 50}
    response = client.post("/api/v1/documents/search", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "ValidationError"


def test_advisor_ask_without_api_key_returns_503():
    """Verifies POST /api/v1/advisor/ask returns 503 when GEMINI_API_KEY is not configured."""
    with patch("app.core.config.Settings.is_gemini_configured", False):
        payload = {"question": "What is the price of gold today?"}
        response = client.post("/api/v1/advisor/ask", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert "Gemini API key is not configured" in data["message"]


def test_advisor_ask_invalid_payload_returns_422():
    """Verifies POST /api/v1/advisor/ask with empty question returns 422 validation error."""
    payload = {"question": ""}
    response = client.post("/api/v1/advisor/ask", json=payload)
    assert response.status_code == 422


def test_advisor_ask_with_mocked_agent_success():
    """Verifies POST /api/v1/advisor/ask returns structured response when agent is active."""
    mock_advisor_resp = AdvisorResponse(
        answer="The current gold spot price is approximately ₹13,061.50 per gram.",
        sources=[],
        market_data=[],
        model="gemini-3.5-flash",
        request_id="test-req-12345",
    )

    with patch("app.services.finance_advisor.finance_advisor_service.advise", new_callable=AsyncMock) as mock_advise:
        mock_advise.return_value = mock_advisor_resp
        payload = {"question": "What is the gold rate in India?"}
        response = client.post("/api/v1/advisor/ask", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == mock_advisor_resp.answer
        assert data["model"] == "gemini-3.5-flash"
        assert data["request_id"] == "test-req-12345"


def test_advisor_ask_rate_limit_returns_429():
    """Verifies POST /api/v1/advisor/ask handles rate limit by returning controlled 429 status."""
    with patch(
        "app.services.finance_advisor.finance_advisor_service.advise",
        side_effect=GeminiRateLimitException("Gemini API rate limit reached. Please wait a moment before sending another request."),
    ):
        payload = {"question": "What is the gold rate in India?"}
        response = client.post("/api/v1/advisor/ask", json=payload)
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "GeminiRateLimitException"
        assert "rate limit" in data["message"].lower()


def test_advisor_ask_quota_exhausted_returns_429():
    """Verifies POST /api/v1/advisor/ask handles quota exhaustion by returning controlled 429 status."""
    with patch(
        "app.services.finance_advisor.finance_advisor_service.advise",
        side_effect=GeminiQuotaExceededException("Gemini API quota has been exhausted. Please verify your project quota or billing."),
    ):
        payload = {"question": "What is the gold rate in India?"}
        response = client.post("/api/v1/advisor/ask", json=payload)
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "GeminiQuotaExceededException"
        assert "quota" in data["message"].lower()
