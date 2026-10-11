"""
Market Data Service.
Fetches and normalizes spot Gold (XAU) and Silver (XAG) prices from Gold-API in INR.
"""
from datetime import datetime, timezone
from typing import Optional
import httpx
from app.core.config import get_settings
from app.core.exceptions import (
    MarketDataUnavailableException,
    UnsupportedAssetException,
)
from app.core.logging import logger
from app.schemas.prices import PriceMetadata, PriceResponse
from app.utils.price_units import (
    convert_troy_ounce_price,
    normalize_asset,
)


class MarketDataService:
    """Service for querying spot precious metal prices with strict validation."""

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: Optional[float] = None):
        settings = get_settings()
        self.base_url = (base_url or settings.gold_api_base_url).rstrip("/")
        self.timeout = timeout_seconds or settings.request_timeout_seconds

    async def get_spot_price(self, asset: str) -> PriceResponse:
        """
        Asynchronously fetches and converts spot market price for gold or silver.
        Raises UnsupportedAssetException if asset alias is unrecognized.
        Raises MarketDataUnavailableException on timeout, network drop, or non-200 status.
        """
        norm = normalize_asset(asset)
        if not norm:
            raise UnsupportedAssetException(asset=asset, supported=["gold", "silver", "xau", "xag"])

        canonical_name, symbol = norm
        url = f"{self.base_url}/price/{symbol}/INR"
        headers = {"User-Agent": "FinanceAdvisorBackend/1.0", "Accept": "application/json"}
        retrieved_at = datetime.now(timezone.utc).isoformat()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception as e:
                    logger.error(f"Malformed JSON from Gold-API: {e}")
                    raise MarketDataUnavailableException(
                        message=f"Invalid JSON response from upstream provider for {canonical_name}",
                        details={"status_code": 200, "parse_error": str(e)},
                    )

                raw_price = data.get("price")
                if raw_price is None or not isinstance(raw_price, (int, float)) or raw_price <= 0:
                    logger.error(f"Invalid or non-numeric price in Gold-API payload: {data}")
                    raise MarketDataUnavailableException(
                        message=f"Invalid or non-positive price received from provider for {canonical_name}",
                        details={"payload": data},
                    )

                # Execute precise unit conversions using Decimal
                conversions = convert_troy_ounce_price(raw_price)

                metadata = PriceMetadata(
                    source="Gold-API",
                    source_updated_at=data.get("updatedAt"),
                    source_updated_at_readable=data.get("updatedAtReadable"),
                    retrieved_at=retrieved_at,
                    exchange_rate_usd_inr=data.get("exchangeRate"),
                )

                formatted = (
                    f"{canonical_name.title()}: ₹{conversions['price_per_gram']:.2f} per gram "
                    f"(₹{conversions['price_per_10g']:.2f} per 10g, ₹{conversions['price_per_troy_ounce']:.2f} per troy ounce). "
                    f"Source: Gold-API ({data.get('updatedAtReadable', 'recent quote')})"
                )

                return PriceResponse(
                    asset=canonical_name.title(),
                    symbol=symbol,
                    currency="INR",
                    currency_symbol="₹",
                    price_per_troy_ounce=conversions["price_per_troy_ounce"],
                    price_per_gram=conversions["price_per_gram"],
                    price_per_10g=conversions["price_per_10g"],
                    price_per_kg=conversions["price_per_kg"],
                    formatted=formatted,
                    metadata=metadata,
                )

            elif response.status_code == 429:
                logger.warning(f"Rate limited by Gold-API: HTTP 429 on {url}")
                raise MarketDataUnavailableException(
                    message="Upstream market data provider rate limit exceeded",
                    details={"status_code": 429},
                )
            else:
                logger.error(f"Gold-API error: HTTP {response.status_code} on {url}")
                raise MarketDataUnavailableException(
                    message=f"Market data provider returned HTTP {response.status_code}",
                    details={"status_code": response.status_code},
                )

        except httpx.TimeoutException as e:
            logger.error(f"Timeout querying Gold-API ({url}): {e}")
            raise MarketDataUnavailableException(
                message=f"Timeout contacting upstream market data provider for {canonical_name}",
                details={"timeout_seconds": self.timeout, "error": str(e)},
            )
        except httpx.RequestError as e:
            logger.error(f"Network error querying Gold-API ({url}): {e}")
            raise MarketDataUnavailableException(
                message=f"Network error connecting to market data provider: {str(e)}",
                details={"error": str(e)},
            )


# Singleton instance
market_data_service = MarketDataService()
