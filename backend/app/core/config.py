"""Application configuration.

All external integrations are optional. If credentials for a provider are
missing, the application falls back to its demo provider rather than
failing to start. Never hardcode secrets here - only environment variable
names and safe defaults.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    app_name: str = "MarketPulse AI"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Provider selection. "demo" is always available and requires no keys.
    market_data_provider: str = "demo"
    news_provider: str = "demo"
    corporate_data_provider: str = "demo"
    broker_provider: str = "none"
    llm_provider: str = "demo"
    notification_provider: str = "none"

    # Optional external credentials (never used if provider == demo/none)
    market_data_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    llm_api_key: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Demo data determinism
    demo_random_seed: int = 42

    # Database / cache (optional - app runs fully in-memory in demo mode)
    database_url: Optional[str] = None
    redis_url: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def provider_status(self) -> dict:
        """Report which providers are live vs demo, and why."""
        return {
            "market_data": self._resolve(self.market_data_provider, self.market_data_api_key),
            "news": self._resolve(self.news_provider, self.news_api_key),
            "corporate_data": self._resolve(self.corporate_data_provider, None),
            "broker": {"mode": self.broker_provider or "none", "live": False},
            "llm": self._resolve(self.llm_provider, self.llm_api_key),
            "notifications": {"mode": self.notification_provider or "none", "live": False},
        }

    @staticmethod
    def _resolve(mode: str, api_key: Optional[str]) -> dict:
        if mode == "demo" or mode == "none":
            return {"mode": "demo", "live": False, "reason": "configured for demo mode"}
        if not api_key:
            return {"mode": "demo", "live": False, "reason": f"{mode} selected but credentials missing; falling back to demo"}
        return {"mode": mode, "live": True, "reason": "credentials present"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
