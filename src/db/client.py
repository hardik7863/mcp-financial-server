"""Supabase client singleton."""

from supabase import Client, create_client

from src.config.env import get_settings

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a singleton Supabase client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client
