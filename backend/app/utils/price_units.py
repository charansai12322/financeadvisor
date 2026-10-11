"""
Financial unit conversions and asset normalization utility.
Uses Decimal arithmetic for accurate rounding without floating point drift.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple

# Standard bullion conversion convention
# 1 troy ounce = 31.1034768 grams, standard convention 31.1035 grams
TROY_OUNCE_TO_GRAMS = Decimal("31.1035")

SUPPORTED_ASSET_ALIASES = {
    "gold": ("gold", "XAU"),
    "xau": ("gold", "XAU"),
    "silver": ("silver", "XAG"),
    "xag": ("silver", "XAG"),
}


def normalize_asset(asset: Optional[str]) -> Optional[Tuple[str, str]]:
    """
    Normalizes asset input to canonical (name, symbol) tuple.
    Returns None if unsupported or invalid.
    Examples:
        'gold' -> ('gold', 'XAU')
        'XAU ' -> ('gold', 'XAU')
        'SILVER' -> ('silver', 'XAG')
        'copper' -> None
    """
    if not asset or not isinstance(asset, str):
        return None
    cleaned = asset.strip().lower()
    return SUPPORTED_ASSET_ALIASES.get(cleaned)


def round_decimal(val: Decimal, places: int = 2) -> Decimal:
    """Rounds a Decimal value to the specified number of decimal places using ROUND_HALF_UP."""
    q = Decimal(10) ** -places
    return val.quantize(q, rounding=ROUND_HALF_UP)


def convert_troy_ounce_price(
    price_troy_ounce: float | Decimal,
    rounding_places: int = 2,
) -> dict:
    """
    Converts a price given per troy ounce into per-gram, per-10-grams, and per-kg prices.
    Uses Decimal arithmetic for accuracy.
    """
    if not isinstance(price_troy_ounce, Decimal):
        price_dec = Decimal(str(price_troy_ounce))
    else:
        price_dec = price_troy_ounce

    price_per_gram = price_dec / TROY_OUNCE_TO_GRAMS
    price_per_10g = price_per_gram * Decimal("10")
    price_per_kg = price_per_gram * Decimal("1000")

    return {
        "price_per_troy_ounce": float(round_decimal(price_dec, rounding_places)),
        "price_per_gram": float(round_decimal(price_per_gram, rounding_places)),
        "price_per_10g": float(round_decimal(price_per_10g, rounding_places)),
        "price_per_kg": float(round_decimal(price_per_kg, rounding_places)),
    }
