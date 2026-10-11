"""
Gemini Model Factory.
Configures and initializes Google Gemini models using verified SDK conventions.
"""
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings
from app.core.exceptions import (
    GeminiInferenceException,
    GeminiUnconfiguredException,
)
from app.core.logging import logger


class GeminiModelFactory:
    """Factory for initializing Google Gemini LLMs."""

    def __init__(self):
        self._settings = get_settings()

    def get_model(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
    ) -> ChatGoogleGenerativeAI:
        """
        Initializes and returns a ChatGoogleGenerativeAI instance.
        Raises GeminiUnconfiguredException if GEMINI_API_KEY is not set.
        Never prints or exposes the API key.
        """
        if not self._settings.is_gemini_configured:
            logger.warning("Attempted to initialize Gemini model without GEMINI_API_KEY configured")
            raise GeminiUnconfiguredException(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your local .env file."
            )

        target_model = model_name or self._settings.gemini_model
        clean_model = target_model.replace("google_genai:", "").strip()

        try:
            return ChatGoogleGenerativeAI(
                model=clean_model,
                api_key=self._settings.gemini_api_key,
                temperature=temperature,
                timeout=self._settings.request_timeout_seconds,
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for model {clean_model}: {e}")
            raise GeminiInferenceException(
                message=f"Failed to initialize Gemini model '{clean_model}'.",
                details={"model": clean_model, "error_type": "initialization_failure"},
            )


gemini_model_factory = GeminiModelFactory()
