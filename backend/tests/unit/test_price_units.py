"""
Unit tests for price units conversion and asset alias normalization.
"""
from decimal import Decimal
import pytest
from app.utils.price_units import (
    convert_troy_ounce_price,
    normalize_asset,
    TROY_OUNCE_TO_GRAMS,
)


def test_asset_normalization_gold_aliases():
    """Verifies that all gold aliases resolve to ('gold', 'XAU')."""
    assert normalize_asset("gold") == ("gold", "XAU")
    assert normalize_asset("GOLD") == ("gold", "XAU")
    assert normalize_asset(" xau ") == ("gold", "XAU")
    assert normalize_asset("XAU") == ("gold", "XAU")


def test_asset_normalization_silver_aliases():
    """Verifies that all silver aliases resolve to ('silver', 'XAG')."""
    assert normalize_asset("silver") == ("silver", "XAG")
    assert normalize_asset("SILVER") == ("silver", "XAG")
    assert normalize_asset(" xag ") == ("silver", "XAG")
    assert normalize_asset("XAG") == ("silver", "XAG")


def test_asset_normalization_unsupported_assets():
    """Verifies unsupported or invalid asset strings return None."""
    assert normalize_asset("copper") is None
    assert normalize_asset("platinum") is None
    assert normalize_asset("") is None
    assert normalize_asset(None) is None
    assert normalize_asset("bitcoin") is None


def test_convert_troy_ounce_price_accuracy():
    """Verifies bullion math using standard 31.1035 divisor."""
    price_oz = 311035.0  # Exactly 10,000 per gram
    res = convert_troy_ounce_price(price_oz)

    assert res["price_per_troy_ounce"] == 311035.0
    assert res["price_per_gram"] == 10000.0
    assert res["price_per_10g"] == 100000.0
    assert res["price_per_kg"] == 10000000.0


def test_convert_troy_ounce_price_rounding():
    """Verifies explicit decimal rounding to 2 places."""
    price_oz = 406258.70
    res = convert_troy_ounce_price(price_oz)

    expected_gram = round(406258.70 / 31.1035, 2)
    expected_10g = round((406258.70 / 31.1035) * 10, 2)

    assert res["price_per_gram"] == expected_gram
    assert res["price_per_10g"] == expected_10g
