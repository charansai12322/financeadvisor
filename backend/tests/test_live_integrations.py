"""
Live Integration Tests.
Executes real network calls against public endpoints (Gold-API, PDF sources).
Validates credentials for Gemini and marks tests BLOCKED if unconfigured.
NEVER fabricates responses or substitutes mocks for real integration tests.
"""
import json
import os
import ssl
import sys
import unittest
import urllib.request
from pathlib import Path

# Ensure backend root is on sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class TestLiveIntegrations(unittest.TestCase):

    def test_live_gold_market_api_connectivity(self):
        """Live integration test: Gold-API XAU/INR endpoint."""
        url = "https://api.gold-api.com/price/XAU/INR"
        req = urllib.request.Request(url, headers={"User-Agent": "FinanceAdvisorAudit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data.get("symbol"), "XAU")
            self.assertEqual(data.get("currency"), "INR")
            price = data.get("price")
            self.assertIsInstance(price, (int, float))
            self.assertGreater(price, 0)
            price_per_gram = price / 31.1035
            print(f"\n[LIVE INTEGRATION PASS] Gold Price: INR {price_per_gram:.2f}/g (INR {price:.2f}/oz, Updated: {data.get('updatedAt')})")

    def test_live_silver_market_api_connectivity(self):
        """Live integration test: Gold-API XAG/INR endpoint."""
        url = "https://api.gold-api.com/price/XAG/INR"
        req = urllib.request.Request(url, headers={"User-Agent": "FinanceAdvisorAudit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode())
            self.assertEqual(data.get("symbol"), "XAG")
            self.assertEqual(data.get("currency"), "INR")
            price = data.get("price")
            self.assertIsInstance(price, (int, float))
            self.assertGreater(price, 0)
            price_per_gram = price / 31.1035
            print(f"\n[LIVE INTEGRATION PASS] Silver Price: INR {price_per_gram:.2f}/g (INR {price:.2f}/oz, Updated: {data.get('updatedAt')})")


    def test_live_cbic_gst_pdf_url_reachability(self):
        """Live integration test: CBIC GST Ready Reckoner PDF source."""
        url = "https://a2ztaxcorp.net/wp-content/uploads/2025/09/CBIC-GST-Ready-Reckoner-indicating-updated-Central-Goods-and-Services-Tax-CGST-rates-on-goods.pdf"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            self.assertEqual(resp.status, 200)
            content_type = resp.headers.get("Content-Type", "")
            self.assertIn("application/pdf", content_type)
            content_length = int(resp.headers.get("Content-Length", 0))
            self.assertGreater(content_length, 500000, "Expected PDF size > 500KB")
            print(f"\n[LIVE INTEGRATION PASS] CBIC GST PDF verified ({content_length} bytes)")

    def test_live_sebi_booklet_pdf_ssl_status(self):
        """
        Live integration test: SEBI Financial Education Booklet SSL inspection.
        Documents whether standard certificate validation succeeds or fails.
        """
        url = "https://investor.sebi.gov.in/pdf/downloadable-documents/Financial%20Education%20Booklet%20-%20English.pdf"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        # First attempt with standard default SSL verification
        ssl_verified = False
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    ssl_verified = True
        except urllib.error.URLError as e:
            # Documenting SSL failure
            self.assertIn("CERTIFICATE_VERIFY_FAILED", str(e))
            print(f"\n[AUDIT FINDING CONFIRMED] SEBI booklet fails default SSL verification: {e}")

        # Second attempt with unverified context to confirm server availability
        unverified_ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=unverified_ctx, timeout=15) as resp:
            self.assertEqual(resp.status, 200)
            content_length = int(resp.headers.get("Content-Length", 0))
            self.assertGreater(content_length, 1000000)
            print(f"[LIVE INTEGRATION PASS] SEBI PDF server reachable via unverified SSL context ({content_length} bytes)")

    def test_live_gemini_api_invocation(self):
        """
        Live integration test: Gemini 3.8 Flash model invocation.
        If GEMINI_API_KEY / GOOGLE_API_KEY is not configured, this test is explicitly BLOCKED.
        """
        from app.core.config import get_settings
        settings = get_settings()
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or settings.gemini_api_key
        if not api_key or not api_key.strip():
            self.skipTest("BLOCKED: GEMINI_API_KEY / GOOGLE_API_KEY environment variable is not configured. Real API call blocked.")

        # If credentials exist, run live generation check
        try:
            from app.services.gemini import gemini_model_factory
            model = gemini_model_factory.get_model()
            resp = model.invoke("Say 'Finance Advisor Ready' and nothing else.")
            content_text = resp.content if isinstance(resp.content, str) else "".join(
                c.get("text", "") if isinstance(c, dict) else str(c) for c in resp.content
            )
            self.assertIn("Finance Advisor Ready", content_text)
            print("\n[LIVE INTEGRATION PASS] Gemini 3.8 Flash invocation passed.")
        except Exception as e:
            self.fail(f"Gemini live invocation failed with error: {e}")



if __name__ == "__main__":
    unittest.main()
