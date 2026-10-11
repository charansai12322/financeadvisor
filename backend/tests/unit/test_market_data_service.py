"""
Unit tests for MarketDataService with mocked upstream responses.
"""
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from app.core.exceptions import (
    MarketDataUnavailableException,
    UnsupportedAssetException,
)
from app.services.market_data import MarketDataService


@pytest.mark.asyncio
async def test_get_spot_price_gold_success():
    """Verifies successful parsing and conversion of Gold XAU mock payload."""
    mock_payload = {
        "symbol": "XAU",
        "name": "Gold",
        "price": 406258.70,
        "currency": "INR",
        "updatedAt": "2026-10-11T14:00:00Z",
        "updatedAtReadable": "just now",
        "exchangeRate": 96.82,
    }

    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        service = MarketDataService(base_url="https://api.gold-api.com", timeout_seconds=5.0)
        res = await service.get_spot_price("gold")

        assert res.asset == "Gold"
        assert res.symbol == "XAU"
        assert res.currency == "INR"
        assert res.price_per_troy_ounce == 406258.70
        assert res.price_per_gram == round(406258.70 / 31.1035, 2)
        assert res.metadata.source_updated_at == "2026-10-11T14:00:00Z"


@pytest.mark.asyncio
async def test_get_spot_price_unsupported_asset():
    """Verifies UnsupportedAssetException is raised for unverified asset names."""
    service = MarketDataService()
    with pytest.raises(UnsupportedAssetException) as exc_info:
        await service.get_spot_price("copper")

    assert "Unsupported asset 'copper'" in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_spot_price_timeout_handling():
    """Verifies timeout raises MarketDataUnavailableException with 502 code."""
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Read timed out")):
        service = MarketDataService(timeout_seconds=2.0)
        with pytest.raises(MarketDataUnavailableException) as exc_info:
            await service.get_spot_price("gold")

        assert "Timeout contacting upstream market data provider" in str(exc_info.value)
        assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_spot_price_rate_limit_429():
    """Verifies HTTP 429 raises rate-limited MarketDataUnavailableException."""
    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 429

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        service = MarketDataService()
        with pytest.raises(MarketDataUnavailableException) as exc_info:
            await service.get_spot_price("silver")

        assert "rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_spot_price_malformed_price():
    """Verifies non-positive or non-numeric price data raises exception."""
    mock_resp = AsyncMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"symbol": "XAU", "price": -50.0}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        service = MarketDataService()
        with pytest.raises(MarketDataUnavailableException) as exc_info:
            await service.get_spot_price("gold")

        assert "Invalid or non-positive price" in str(exc_info.value)
