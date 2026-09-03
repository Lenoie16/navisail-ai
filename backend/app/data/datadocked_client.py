"""Centralized, bounded Data Docked HTTP client.

Endpoint paths are configuration-driven so the current provider OpenAPI remains
the runtime authority rather than being duplicated across domain modules.
"""

from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime
from time import monotonic
from typing import Any

import httpx

from app.core.config import settings


class DataDockedError(RuntimeError):
    """A provider error safe to expose without credentials or headers."""


class DataDockedProvider:
    name = "DATADOCKED"

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._last_success: datetime | None = None
        self._last_failure: datetime | None = None
        self._last_error: str | None = None
        self._status = "DISABLED" if not settings.datadocked_enabled else "UNAVAILABLE"
        self._credits: int | None = None

    async def _request(self, path: str, cache_key: str, **params: str) -> dict[str, Any]:
        cached = self._cache.get(cache_key)
        now = monotonic()
        if cached and now - cached[0] <= settings.datadocked_cache_ttl_seconds:
            return {**cached[1], "_provider_cache": True}
        if not settings.datadocked_enabled:
            if cached and settings.datadocked_fail_open_to_cache:
                return {**cached[1], "_provider_cache": True}
            raise DataDockedError("Data Docked provider is disabled")
        if settings.datadocked_credit_guard_enabled and self._credits is not None:
            if self._credits < settings.datadocked_min_credits_required:
                self._status = "LOW_CREDITS" if self._credits else "CREDITS_EXHAUSTED"
                if cached and settings.datadocked_fail_open_to_cache:
                    return {**cached[1], "_provider_cache": True}
                raise DataDockedError("Data Docked credit guard prevented the request")
        client = self._client
        owns_client = client is None
        if client is None:
            timeout = httpx.Timeout(
                settings.datadocked_request_timeout_seconds,
                connect=settings.datadocked_connect_timeout_seconds,
            )
            client = httpx.AsyncClient(
                base_url=settings.datadocked_base_url.rstrip("/"),
                timeout=timeout,
                headers={"x-api-key": settings.datadocked_api_key or ""},
            )
        try:
            for attempt in range(settings.datadocked_max_retries + 1):
                try:
                    request_url = path
                    if not str(client.base_url):
                        request_url = f"{settings.datadocked_base_url.rstrip('/')}{path}"
                    response = await client.get(request_url, params=params)
                    if response.status_code == 429:
                        self._status = "RATE_LIMITED"
                        raise DataDockedError("Data Docked rate limit reached")
                    if response.status_code in {401, 403}:
                        self._status = "UNAVAILABLE"
                        raise DataDockedError("Data Docked authentication failed")
                    if response.status_code >= 500 and attempt < settings.datadocked_max_retries:
                        await asyncio.sleep(
                            settings.datadocked_backoff_base_seconds * (2**attempt)
                            + random.random()
                        )
                        continue
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, dict):
                        raise DataDockedError("Data Docked returned an invalid response")
                    self._cache[cache_key] = (monotonic(), payload)
                    self._last_success = datetime.now(UTC)
                    self._last_error = None
                    self._status = "HEALTHY"
                    return payload
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt == settings.datadocked_max_retries:
                        raise DataDockedError("Data Docked request timed out or failed") from exc
                    await asyncio.sleep(
                        settings.datadocked_backoff_base_seconds * (2**attempt) + random.random()
                    )
        except (DataDockedError, httpx.HTTPError) as exc:
            self._last_failure = datetime.now(UTC)
            self._last_error = str(exc)
            if cached and settings.datadocked_fail_open_to_cache:
                return {**cached[1], "_provider_cache": True}
            if isinstance(exc, DataDockedError):
                raise
            raise DataDockedError("Data Docked request failed") from exc
        finally:
            if owns_client:
                await client.aclose()
        raise DataDockedError("Data Docked request failed")

    async def get_vessel_location(self, identifier: str) -> dict[str, Any]:
        return await self._request(
            "/vessels/location", f"location:{identifier}", identifier=identifier
        )

    async def get_vessel_details(self, identifier: str) -> dict[str, Any]:
        return await self._request(
            "/vessels/details", f"details:{identifier}", identifier=identifier
        )

    async def get_vessel_history(self, identifier: str, date_range: str) -> dict[str, Any]:
        return await self._request(
            "/vessels/history",
            f"history:{identifier}:{date_range}",
            identifier=identifier,
            range=date_range,
        )

    async def get_vessels_by_area(self, area: dict[str, float]) -> dict[str, Any]:
        if not (
            -90 <= area["min_lat"] <= area["max_lat"] <= 90
            and -180 <= area["min_lon"] <= area["max_lon"] <= 180
        ):
            raise ValueError("invalid geographic area")
        return await self._request(
            "/vessels/area", f"area:{sorted(area.items())}", **{k: str(v) for k, v in area.items()}
        )

    async def get_port_calls(self, identifier: str, *, by_port: bool = False) -> dict[str, Any]:
        kind = "port" if by_port else "vessel"
        return await self._request(
            f"/port-calls/{kind}", f"port-calls:{kind}:{identifier}", identifier=identifier
        )

    async def get_route(self, origin: str, destination: str) -> dict[str, Any]:
        return await self._request(
            "/routes", f"route:{origin}:{destination}", origin=origin, destination=destination
        )

    async def health(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "enabled": settings.datadocked_enabled,
            "configured": bool(settings.datadocked_api_key and settings.datadocked_base_url),
            "reachable": self._last_success is not None,
            "status": self._status,
            "last_success": self._last_success,
            "last_failure": self._last_failure,
            "last_error": self._last_error,
            "credits": self._credits,
        }


datadocked_provider = DataDockedProvider()

__all__ = ["DataDockedError", "DataDockedProvider", "datadocked_provider"]
