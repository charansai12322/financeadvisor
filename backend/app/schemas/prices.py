"""
Market prices response schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field


class PriceMetadata(BaseModel):
    """Metadata regarding upstream provider, timestamps, and market conventions."""
    source: str = Field(default="Gold-API", description="Upstream pricing provider")
    source_updated_at: Optional[str] = Field(default=None, description="ISO-8601 UTC timestamp from provider")
    source_updated_at_readable: Optional[str] = Field(default=None, description="Human-readable relative time")
    retrieved_at: str = Field(description="ISO-8601 UTC timestamp of backend retrieval")
    exchange_rate_usd_inr: Optional[float] = Field(default=None, description="Reported exchange rate")
    market_note: str = Field(
        default="Spot bullion price. Excludes retail making charges, local dealer premiums, and GST (3%).",
        description="Market context distinction between spot rate and jewellery retail cost",
    )


class PriceResponse(BaseModel):
    """Spot commodity price response with explicit units."""
    asset: str = Field(description="Normalized asset name (Gold or Silver)")
    symbol: str = Field(description="Commodity symbol (XAU or XAG)")
    currency: str = Field(default="INR", description="Currency code")
    currency_symbol: str = Field(default="₹", description="Currency display symbol")
    price_per_troy_ounce: float = Field(description="Spot price per troy ounce (31.1035 grams)")
    price_per_gram: float = Field(description="Calculated spot price per gram")
    price_per_10g: float = Field(description="Standard Indian market unit: price per 10 grams")
    price_per_kg: float = Field(description="Calculated spot price per kilogram (1000 grams)")
    formatted: str = Field(description="Human-readable summary string")
    metadata: PriceMetadata = Field(description="Source provenance and timestamp metadata")
