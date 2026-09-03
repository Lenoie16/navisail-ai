"""Centralized application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Navisail AI"
    app_version: str = "0.1.0-rc.1"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://navisail:navisail@localhost:5432/navisail"
    redis_url: str = "redis://localhost:6379/0"
    redis_health_timeout_seconds: float = 2.0
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    log_level: str = "INFO"
    demo_mode: bool = True
    navisail_mode: Literal["DEMO", "SYNTHETIC", "LIVE"] = "DEMO"
    timezone: str = "UTC"
    enable_docs: bool = True
    auth_required: bool = False
    auth_token: str | None = None
    rate_limit_per_minute: int = 120
    error_tracking_dsn: str | None = None
    worker_heartbeat_seconds: float = 10.0
    datadocked_enabled: bool = False
    datadocked_api_key: str | None = None
    datadocked_base_url: str = "https://api.datadocked.com"
    datadocked_request_timeout_seconds: float = 15.0
    datadocked_connect_timeout_seconds: float = 5.0
    datadocked_max_retries: int = 3
    datadocked_backoff_base_seconds: float = 1.0
    datadocked_cache_ttl_seconds: int = 300
    datadocked_credit_guard_enabled: bool = True
    datadocked_min_credits_required: int = 10
    datadocked_fail_open_to_cache: bool = True
    datadocked_fallback_to_synthetic: bool = False
    datadocked_live_tests: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable configuration snapshot."""
    return Settings()


settings = get_settings()
