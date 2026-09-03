"""Model monitoring records and degradation decisions."""

from datetime import UTC, datetime
from pydantic import BaseModel, Field


class MonitoringRecord(BaseModel):
    model_name: str
    model_version: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    prediction_error: float | None = Field(default=None, ge=0)
    drift_score: float | None = Field(default=None, ge=0)
    data_freshness_hours: float | None = Field(default=None, ge=0)
    feature_changes: tuple[str, ...] = ()
    performance_degraded: bool = False
    reason: str | None = None


class MonitoringService:
    def __init__(self) -> None:
        self._records: list[MonitoringRecord] = []

    def record(self, record: MonitoringRecord) -> MonitoringRecord:
        self._records.append(record)
        return record

    def for_model(self, model_name: str, version: str) -> tuple[MonitoringRecord, ...]:
        return tuple(r for r in self._records if r.model_name == model_name and r.model_version == version)


monitoring_service = MonitoringService()
