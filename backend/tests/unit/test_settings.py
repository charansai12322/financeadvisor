"""
Unit tests for Settings parsing, CORS handling, and validation.
"""
import pytest
from app.core.config import Settings


def test_settings_default_values():
    """Verifies default values and types for core settings."""
    settings = Settings(
        gemini_api_key=None,
        _env_file=None,
    )
    assert settings.app_env == "development"
    assert settings.app_port == 8000
    assert settings.gemini_model == "gemini-3.5-flash"
    assert settings.request_timeout_seconds == 10.0
    assert settings.is_gemini_configured is False


def test_settings_cors_parsing():
    """Verifies parsing of comma-separated CORS origins."""
    settings = Settings(
        cors_origins="http://localhost:3000, https://myfrontend.vercel.app , http://127.0.0.1:3000",
        _env_file=None,
    )
    parsed = settings.parsed_cors_origins
    assert len(parsed) == 3
    assert "http://localhost:3000" in parsed
    assert "https://myfrontend.vercel.app" in parsed
    assert "http://127.0.0.1:3000" in parsed


def test_settings_port_validation():
    """Verifies port boundary validation (1 to 65535)."""
    with pytest.raises(ValueError):
        Settings(app_port=0, _env_file=None)

    with pytest.raises(ValueError):
        Settings(app_port=70000, _env_file=None)


def test_settings_timeout_validation():
    """Verifies timeout must be positive."""
    with pytest.raises(ValueError):
        Settings(request_timeout_seconds=-1.0, _env_file=None)
