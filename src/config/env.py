"""Environment configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon or service-role key")

    mcp_transport: str = Field("stdio", description="Transport: stdio or sse")
    mcp_host: str = Field("0.0.0.0", description="SSE host")
    mcp_port: int = Field(8000, description="SSE port")

    rate_limit_rpm: int = Field(60, description="Rate limit requests per minute")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
