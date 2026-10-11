"""
Unit tests for Gemini model configuration and validation.
Audits model identifier strings, environment variable resolution, and authentication checks.
"""
import unittest
import os
from unittest.mock import patch


# Config helper
def resolve_gemini_credentials():
    """
    Resolves Gemini API credentials cleanly across environments:
    Checks GEMINI_API_KEY, then GOOGLE_API_KEY, then legacy SEC1.
    Never exposes key values.
    """
    for var_name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "sec1"]:
        val = os.environ.get(var_name)
        if val and val.strip():
            return {
                "configured": True,
                "source_variable": var_name,
                "api_key": val.strip(),
            }
    return {
        "configured": False,
        "source_variable": None,
        "api_key": None,
        "error": "No Gemini API key found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in environment.",
    }


def validate_gemini_model_id(model_id_str: str) -> dict:
    """
    Validates model identifier string.
    Ensures model belongs to verified official Gemini models.
    """
    # Strip optional provider prefix like 'google_genai:'
    clean_id = model_id_str.replace("google_genai:", "").strip()

    # Official known Gemini models
    known_official_models = {
        "gemini-3.5-flash": "Gemini 3.5 Flash (Verified Google Gemini model)",
        "gemini-3.5-flash-lite": "Gemini 3.5 Flash Lite",
        "gemini-3.8-flash": "Gemini 3.8 Flash (High-performance workhorse model, released Sept 2026)",
        "gemini-3.8-flash-lite": "Gemini 3.8 Flash Lite",
        "gemini-2.0-flash": "Gemini 2.0 Flash",
        "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
        "gemini-1.5-flash": "Gemini 1.5 Flash",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
    }

    if clean_id in known_official_models:
        return {
            "valid": True,
            "canonical_id": clean_id,
            "description": known_official_models[clean_id],
            "langchain_init_string": f"google_genai:{clean_id}",
        }
    else:
        return {
            "valid": False,
            "canonical_id": clean_id,
            "error": f"Model identifier '{clean_id}' is not a verified Google Gemini model. Available models: {list(known_official_models.keys())}",
        }


class TestGeminiConfig(unittest.TestCase):

    def test_invalid_model_id_is_rejected(self):
        """Reject unverified or nonexistent model identifiers."""
        res = validate_gemini_model_id("google_genai:gemini-unknown-fake-model")
        self.assertFalse(res["valid"])
        self.assertIn("not a verified Google Gemini model", res["error"])

    def test_requested_gemini_3_5_flash_is_valid(self):
        """The requested Gemini 3.5 Flash maps to official model id 'gemini-3.5-flash'."""
        res = validate_gemini_model_id("gemini-3.5-flash")
        self.assertTrue(res["valid"])
        self.assertEqual(res["canonical_id"], "gemini-3.5-flash")
        self.assertEqual(res["langchain_init_string"], "google_genai:gemini-3.5-flash")

    def test_requested_gemini_3_8_flash_is_valid(self):
        """The Gemini 3.8 Flash maps to official model id 'gemini-3.8-flash'."""
        res = validate_gemini_model_id("gemini-3.8-flash")
        self.assertTrue(res["valid"])
        self.assertEqual(res["canonical_id"], "gemini-3.8-flash")
        self.assertEqual(res["langchain_init_string"], "google_genai:gemini-3.8-flash")

    def test_credential_resolution_with_gemini_api_key(self):
        """Resolves GEMINI_API_KEY properly."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-abc"}, clear=True):
            creds = resolve_gemini_credentials()
            self.assertTrue(creds["configured"])
            self.assertEqual(creds["source_variable"], "GEMINI_API_KEY")
            self.assertEqual(creds["api_key"], "test-key-abc")

    def test_credential_resolution_fallback_to_google_api_key(self):
        """Falls back to GOOGLE_API_KEY if GEMINI_API_KEY is unset."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key"}, clear=True):
            creds = resolve_gemini_credentials()
            self.assertTrue(creds["configured"])
            self.assertEqual(creds["source_variable"], "GOOGLE_API_KEY")

    def test_credential_resolution_missing_keys(self):
        """Handles missing API keys with informative message without crashing."""
        with patch.dict(os.environ, {}, clear=True):
            creds = resolve_gemini_credentials()
            self.assertFalse(creds["configured"])
            self.assertIn("No Gemini API key found", creds["error"])


if __name__ == "__main__":
    unittest.main()
