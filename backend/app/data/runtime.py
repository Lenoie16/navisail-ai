"""Runtime data-mode and provider status contract."""

from typing import Literal

from pydantic import BaseModel

from app.core.config import settings


class RuntimeDataStatus(BaseModel):
    mode: Literal["DEMO", "SYNTHETIC", "LIVE"]
    primary_provider: str
    fallback_provider: str | None
    fallback_enabled: bool
    approval_requires_authoritative_data: bool


async def runtime_data_status() -> RuntimeDataStatus:
    """Return the effective data policy without exposing provider credentials."""

    provider_ready = bool(
        settings.datadocked_enabled
        and settings.datadocked_api_key
        and settings.datadocked_base_url
    )
    primary_provider = "DATADOCKED" if settings.navisail_mode == "LIVE" and provider_ready else (
        "SYNTHETIC" if settings.navisail_mode == "SYNTHETIC" else "DEMO"
    )
    fallback_enabled = (
        settings.datadocked_fallback_to_synthetic and settings.navisail_mode == "LIVE"
    )
    return RuntimeDataStatus(
        mode=settings.navisail_mode,
        primary_provider=primary_provider,
        fallback_provider="SYNTHETIC" if fallback_enabled else None,
        fallback_enabled=fallback_enabled,
        approval_requires_authoritative_data=True,
    )
