from datetime import UTC, datetime, timedelta

import app.data.datadocked_client as client_module
import httpx
import pytest
from app.core.config import Settings
from app.data.datadocked import DataDockedError, DataDockedProvider, map_vessel_location


def test_datadocked_mapping_assigns_live_status_and_canonical_units() -> None:
    record = map_vessel_location(
        {
            "imo": "1234567",
            "latitude": 20,
            "longitude": 70,
            "speed": 12.5,
            "course": 90,
            "observed_at": (datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
        }
    )
    assert record.status == "LIVE"
    assert record.normalized_payload.vessel_id == "1234567"
    assert record.normalized_payload.speed_knots == 12.5
    assert record.lineage.connector_name == "datadocked"


def test_datadocked_mapping_rejects_unresolved_identity() -> None:
    with pytest.raises(ValueError, match="no IMO or MMSI"):
        map_vessel_location(
            {
                "latitude": 20,
                "longitude": 70,
                "observed_at": datetime.now(UTC).isoformat(),
            }
        )


@pytest.mark.asyncio
async def test_datadocked_client_uses_cache_after_first_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        client_module,
        "settings",
        Settings(datadocked_enabled=True, datadocked_api_key="test-key"),
    )
    calls = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json={"latitude": 1, "longitude": 2, "observed_at": datetime.now(UTC).isoformat()},
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = DataDockedProvider(client)
    assert (await provider.get_vessel_location("1234567"))["latitude"] == 1
    assert (await provider.get_vessel_location("1234567"))["_provider_cache"] is True
    assert calls == 1
    await client.aclose()


@pytest.mark.asyncio
async def test_datadocked_client_does_not_retry_rate_limits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        client_module,
        "settings",
        Settings(datadocked_enabled=True, datadocked_api_key="test-key", datadocked_max_retries=3),
    )

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = DataDockedProvider(client)
    with pytest.raises(DataDockedError, match="rate limit"):
        await provider.get_vessel_location("1234567")
    assert (await provider.health())["status"] == "RATE_LIMITED"
    await client.aclose()
