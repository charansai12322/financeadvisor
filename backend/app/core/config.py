"""
Central Application Settings Module.
Loads and validates typed environment configuration using Pydantic Settings.
Robustly resolves project-relative paths regardless of invocation working directory.
"""
from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine backend root directory (anchor for relative paths)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def find_env_file() -> str:
    """Finds .env file checking backend directory first, then current working directory."""
    candidates = [
        BACKEND_DIR / ".env",
        Path(".env"),
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return str(c.resolve())
    # Default to backend/.env even if missing so settings can load defaults
    return str((BACKEND_DIR / ".env").resolve())


class Settings(BaseSettings):
    """
    Central typed settings loaded from environment variables and .env file.
    Does not crash if GEMINI_API_KEY is empty so that non-agent endpoints
    (health, prices, document status) remain fully functional.
    """
    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Gemini AI Configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API Key for model orchestration",
    )
    gemini_model: str = Field(
        default="gemini-3.5-flash",
        description="Verified Gemini Model identifier",
    )

    # Upstream Market Data API
    gold_api_base_url: str = Field(
        default="https://api.gold-api.com",
        description="Base URL for Gold and Silver spot price API",
    )

    # Application Server Settings
    app_env: str = Field(default="development", description="Application environment")
    app_host: str = Field(default="127.0.0.1", description="Server host interface")
    app_port: int = Field(default=8000, description="Server port")

    # CORS Settings
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Network Timeouts
    request_timeout_seconds: float = Field(
        default=10.0,
        description="Default timeout for upstream HTTP requests in seconds",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging severity level")

    # Vector Database & Document Storage
    chroma_persist_directory: str = Field(
        default=str((BACKEND_DIR / "chroma_langchain_db").resolve()),
        description="Filesystem path for persistent Chroma DB",
    )
    chroma_collection_name: str = Field(
        default="finance_docs",
        description="Chroma collection name for financial documents",
    )
    pdf_storage_dir: str = Field(
        default=str((BACKEND_DIR / "data" / "pdfs").resolve()),
        description="Directory for cached PDF reference documents",
    )

    @field_validator("app_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v

    @field_validator("request_timeout_seconds")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Request timeout must be positive, got {v}")
        return v

    @field_validator("gemini_api_key")
    @classmethod
    def sanitize_api_key(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return None

    @field_validator("chroma_persist_directory", "pdf_storage_dir")
    @classmethod
    def resolve_relative_paths(cls, v: str) -> str:
        p = Path(v)
        if not p.is_absolute():
            return str((BACKEND_DIR / p).resolve())
        return str(p.resolve())

    @property
    def parsed_cors_origins(self) -> List[str]:
        """Parses comma-separated cors_origins string into a list of clean URLs."""
        if not self.cors_origins:
            return ["*"] if self.app_env == "development" else []
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_gemini_configured(self) -> bool:
        """Returns True only if a non-empty Gemini API key is configured."""
        return bool(self.gemini_api_key and len(self.gemini_api_key.strip()) > 0)


@lru_cache
def get_settings() -> Settings:
    """Returns singleton cached instance of application settings."""
    return Settings()
