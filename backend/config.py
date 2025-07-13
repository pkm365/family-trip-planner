"""
Configuration management using Pydantic Settings.

Loads environment variables with proper validation and defaults.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database configuration
    database_url: str = Field(
        default="sqlite:///./trip_planner.db",
        env="DATABASE_URL",
        description="Database connection URL",
    )

    # External API keys
    openweather_api_key: str = Field(
        default="",
        env="OPENWEATHER_API_KEY",
        description="OpenWeatherMap API key",
    )

    google_places_api_key: str = Field(
        default="",
        env="GOOGLE_PLACES_API_KEY",
        description="Google Places API key",
    )

    # Application settings
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode",
    )

    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY",
        description="Secret key for session management",
    )

    # CORS settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080,http://127.0.0.1:8000",
        env="ALLOWED_ORIGINS",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def origins_list(self) -> list[str]:
        """Return allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
