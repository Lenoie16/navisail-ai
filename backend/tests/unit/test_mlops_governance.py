from datetime import UTC, datetime

import pytest

from app.mlops.evaluation import chronological_validation
from app.mlops.registry import ModelLifecycle, ModelRecord, ModelRegistry


def _model(*, degraded: bool = False, approval_status: str = "pending") -> ModelRecord:
    return ModelRecord(
        model_name="freight",
        version="2026.09",
        training_date=datetime(2026, 9, 1, tzinfo=UTC),
        training_window="2026-01-01/2026-08-31",
        features=("route", "vessel_class"),
        hyperparameters={"window": 7},
        metrics={"mae": 4.2},
        artifact_location="registry://freight/2026.09",
        degraded=degraded,
        approval_status=approval_status,
    )


def test_registry_requires_approval_and_blocks_degraded_activation() -> None:
    registry = ModelRegistry()
    registry.register(_model())
    registry.promote("freight", "2026.09", ModelLifecycle.CANDIDATE)
    with pytest.raises(PermissionError):
        registry.promote("freight", "2026.09", ModelLifecycle.APPROVED)
    registry.get("freight", "2026.09").approval_status = "approved"
    registry.promote("freight", "2026.09", ModelLifecycle.APPROVED)

    degraded = _model(degraded=True, approval_status="approved").model_copy(update={"version": "2026.10"})
    registry.register(degraded)
    registry.promote("freight", "2026.10", ModelLifecycle.CANDIDATE)
    registry.promote("freight", "2026.10", ModelLifecycle.APPROVED)
    with pytest.raises(ValueError, match="degraded"):
        registry.promote("freight", "2026.10", ModelLifecycle.ACTIVE)


def test_chronological_evaluation_reports_residuals_and_benchmark() -> None:
    metrics = chronological_validation([10, 12, 14], [9, 11, 15], benchmark=[8, 10, 13])
    assert metrics["residuals"] == [1, 1, -1]
    assert metrics["benchmark_mae"] > metrics["mae"]
