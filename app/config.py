"""
app/config.py
=============
Centralized application configuration via Pydantic BaseSettings.
All values are loaded from environment variables or the .env file.
No hardcoded configuration values are present in this module.
"""
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application --------------------------------------------------------
    app_name: str = Field(default="Rice Disease API")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    # ---- Server -------------------------------------------------------------
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # ---- Model Paths --------------------------------------------------------
    model_path: Path = Field(default=Path("models/mobilenetv2_padi.pth"))
    labels_path: Path = Field(default=Path("models/labels.json"))
    metadata_path: Path = Field(default=Path("models/metadata.json"))

    # ---- Image Upload Constraints -------------------------------------------
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: str = Field(default="jpg,jpeg,png,webp")

    # ---- CORS ---------------------------------------------------------------
    cors_origins: str = Field(default="*")

    # ---- Future: LLM Integration -------------------------------------------
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o")

    # ---- Derived Properties -------------------------------------------------
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes for upload size validation."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Return allowed extensions as a list of lowercase strings."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Singleton settings instance used throughout the application
settings = Settings()
