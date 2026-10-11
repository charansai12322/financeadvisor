"""
Unit tests for Gold and Silver Market Data integration.
Tests response parsing, unit conversions, error handling, and timeout behavior.
Uses mocks to remain completely deterministic and independent of external package availability.
"""
import unittest
import sys
from unittest.mock import MagicMock

# Setup mock requests in sys.modules if requests is not installed in the environment
if "requests" not in sys.modules:
    try:
        import requests
    except ModuleNotFoundError:
        mock_requests = MagicMock()
        mock_requests_exceptions = MagicMock()

        class RequestException(Exception):
            pass

        class ConnectionError(RequestException):
            pass

        class Timeout(RequestException):
            pass

        mock_requests_exceptions.RequestException = RequestException
        mock_requests_exceptions.ConnectionError = ConnectionError
        mock_requests_exceptions.Timeout = Timeout

        mock_requests.exceptions = mock_requests_exceptions
        mock_requests.RequestException = RequestException
        mock_requests.ConnectionError = ConnectionError
        mock_requests.Timeout = Timeout

        sys.modules["requests"] = mock_requests
        sys.modules["requests.exceptions"] = mock_requests_exceptions

import requests


# Exact logic extracted from Cell 10 of notebook
def original_get_market_price(asset: str) -> str:
    symbols = {
        "gold": "XAU",
        "silver": "XAG",
    }
    symbol = symbols.get(asset.lower())
    if not symbol:
        return "Supported assets: gold, silver"

    url = f"https://api.gold-api.com/price/{symbol}/INR"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data.get("price")
        if price:
            price_per_gram = price / 31.1035
            return f"{asset.title()}: ₹{price_per_gram:.2f} per gram (₹{price:.2f} per troy ounce). Source: Gold-API"
    return f"Could not fetch price for {asset}"


# Hardened production-grade version addressing defects found during audit
def hardened_get_market_price(asset: str, timeout: float = 10.0) -> dict:
    if not asset or not isinstance(asset, str):
        return {"error": "Invalid asset input. Supported assets: gold, silver", "status": "error"}

    cleaned_asset = asset.strip().lower()
    symbols = {
        "gold": "XAU",
        "silver": "XAG",
    }
    symbol = symbols.get(cleaned_asset)
    if not symbol:
        return {"error": f"Unsupported asset '{asset}'. Supported assets: gold, silver", "status": "error"}

    url = f"https://api.gold-api.com/price/{symbol}/INR"
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "FinanceAdvisorBackend/1.0"})
        if response.status_code == 200:
            data = response.json()
            price = data.get("price")
            if price is not None and isinstance(price, (int, float)) and price > 0:
                troy_ounce_to_grams = 31.1035
                price_per_gram = price / troy_ounce_to_grams
                price_per_10g = price_per_gram * 10
                return {
                    "asset": cleaned_asset.title(),
                    "symbol": symbol,
                    "currency": data.get("currency", "INR"),
                    "price_per_troy_ounce": round(price, 2),
                    "price_per_gram": round(price_per_gram, 2),
                    "price_per_10g": round(price_per_10g, 2),
                    "updated_at": data.get("updatedAt"),
                    "updated_at_readable": data.get("updatedAtReadable"),
                    "source": "Gold-API",
                    "formatted": (
                        f"{cleaned_asset.title()}: ₹{price_per_gram:.2f} per gram "
                        f"(₹{price_per_10g:.2f} per 10g, ₹{price:.2f} per troy ounce). "
                        f"Source: Gold-API ({data.get('updatedAtReadable', 'recently')})"
                    ),
                    "status": "success",
                }
            return {"error": f"Malformed or non-numeric price data in API response for {cleaned_asset}", "status": "error"}
        elif response.status_code == 429:
            return {"error": "Rate limit exceeded on Gold-API provider", "status": "rate_limited"}
        else:
            return {"error": f"Provider error: HTTP status {response.status_code}", "status": "provider_error"}
    except requests.exceptions.Timeout:
        return {"error": f"Connection timed out fetching price for {cleaned_asset}", "status": "timeout"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error fetching price for {cleaned_asset}: {str(e)}", "status": "network_error"}
    except ValueError as e:
        return {"error": f"Failed to parse JSON response: {str(e)}", "status": "parse_error"}


class TestMarketData(unittest.TestCase):

    def test_original_parsing_gold_success(self):
        """Test original function successfully parses mock Gold XAU response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "XAU",
            "name": "Gold",
            "price": 406258.70,
            "currency": "INR",
            "updatedAt": "2026-10-11T13:52:37Z",
        }
        requests.get = MagicMock(return_value=mock_response)

        result = original_get_market_price("gold")
        expected_per_gram = 406258.70 / 31.1035
        self.assertIn("Gold:", result)
        self.assertIn(f"₹{expected_per_gram:.2f} per gram", result)
        self.assertIn("₹406258.70 per troy ounce", result)

    def test_original_parsing_silver_success(self):
        """Test original function successfully parses mock Silver XAG response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "XAG",
            "name": "Silver",
            "price": 5900.00,
            "currency": "INR",
            "updatedAt": "2026-10-11T13:52:37Z",
        }
        requests.get = MagicMock(return_value=mock_response)

        result = original_get_market_price("silver")
        expected_per_gram = 5900.00 / 31.1035
        self.assertIn("Silver:", result)
        self.assertIn(f"₹{expected_per_gram:.2f} per gram", result)

    def test_original_unsupported_asset(self):
        """Test original function rejects unsupported asset."""
        result = original_get_market_price("copper")
        self.assertEqual(result, "Supported assets: gold, silver")

    def test_original_whitespace_failure(self):
        """Original function fails if asset contains whitespace like 'gold '."""
        result = original_get_market_price("gold ")
        self.assertEqual(result, "Supported assets: gold, silver", "Original function fails to strip whitespace")

    def test_original_network_exception_crash(self):
        """Original function has no try/except and crashes on requests.exceptions.ConnectionError."""
        requests.get = MagicMock(side_effect=requests.exceptions.ConnectionError("Network disconnected"))
        with self.assertRaises(requests.exceptions.ConnectionError):
            original_get_market_price("gold")

    def test_original_timeout_crash(self):
        """Original function crashes on requests.exceptions.Timeout."""
        requests.get = MagicMock(side_effect=requests.exceptions.Timeout("Request timed out"))
        with self.assertRaises(requests.exceptions.Timeout):
            original_get_market_price("gold")

    def test_hardened_success_and_10g_calculation(self):
        """Hardened function accurately calculates per gram and per 10g prices with metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "XAU",
            "name": "Gold",
            "price": 406258.70,
            "currency": "INR",
            "updatedAt": "2026-10-11T13:52:37Z",
            "updatedAtReadable": "a few seconds ago",
        }
        requests.get = MagicMock(return_value=mock_response)

        res = hardened_get_market_price("  gold  ")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["asset"], "Gold")
        self.assertAlmostEqual(res["price_per_gram"], 406258.70 / 31.1035, places=2)
        self.assertAlmostEqual(res["price_per_10g"], (406258.70 / 31.1035) * 10, places=2)
        self.assertEqual(res["updated_at"], "2026-10-11T13:52:37Z")

    def test_hardened_graceful_timeout_handling(self):
        """Hardened function catches timeout and returns structured error instead of crashing."""
        requests.get = MagicMock(side_effect=requests.exceptions.Timeout("Read timeout"))
        res = hardened_get_market_price("gold")
        self.assertEqual(res["status"], "timeout")
        self.assertIn("Connection timed out", res["error"])

    def test_hardened_graceful_network_error_handling(self):
        """Hardened function catches network connection failure and returns structured error."""
        requests.get = MagicMock(side_effect=requests.exceptions.ConnectionError("Connection refused"))
        res = hardened_get_market_price("silver")
        self.assertEqual(res["status"], "network_error")
        self.assertIn("Network error", res["error"])

    def test_hardened_rate_limiting_429(self):
        """Hardened function identifies HTTP 429 rate limit."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        requests.get = MagicMock(return_value=mock_response)
        res = hardened_get_market_price("gold")
        self.assertEqual(res["status"], "rate_limited")


if __name__ == "__main__":
    unittest.main()
