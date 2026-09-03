import app.data.runtime as runtime_module
import pytest
from app.core.config import Settings


@pytest.mark.asyncio
async def test_runtime_status_requires_authoritative_data_for_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        runtime_module,
        "settings",
        Settings(
            navisail_mode="LIVE",
            datadocked_enabled=True,
            datadocked_api_key="test-key",
            datadocked_fallback_to_synthetic=True,
        ),
    )
    status = await runtime_module.runtime_data_status()
    assert status.mode == "LIVE"
    assert status.primary_provider == "DATADOCKED"
    assert status.fallback_provider == "SYNTHETIC"
    assert status.approval_requires_authoritative_data is True
