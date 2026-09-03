"""Registry and orchestration boundary for source ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from app.data.connectors import SourceConnector
from app.data.contracts import (
    AISVesselPayload,
    BerthPayload,
    DataDomain,
    FreightMarketPayload,
    FuelPayload,
    FXPayload,
    InventoryPayload,
    NewsGeopoliticalPayload,
    PayloadModel,
    PortPayload,
    RouteReferencePayload,
    SourceRecord,
    WeatherPayload,
)
from app.data.freshness import evaluate_freshness
from app.data.normalize import normalize_record_payload
from app.data.validation import ValidationIssue, validate_record


class QuarantinedRecord(BaseModel):
    source: str | None = None
    source_identifier: str | None = None
    reason: tuple[ValidationIssue, ...]
    raw: Any = None
    quarantined_at: datetime


class IngestionResult(BaseModel):
    accepted: int = 0
    quarantined: int = 0
    quarantined_records: tuple[QuarantinedRecord, ...] = ()


class SourceRegistry:
    """In-memory registry used by the API and tests.

    Persistence is deliberately outside Phase 3; this boundary can be replaced
    by a repository without changing connectors or contracts.
    """

    def __init__(self) -> None:
        self.records: dict[tuple[str, str], SourceRecord[Any]] = {}
        self.quarantine: list[QuarantinedRecord] = []
        self.connectors: dict[str, SourceConnector] = {}

    def register_connector(self, connector: SourceConnector) -> None:
        self.connectors[connector.name] = connector

    def register(
        self,
        record: SourceRecord[Any],
        *,
        now: datetime | None = None,
    ) -> tuple[bool, tuple[ValidationIssue, ...]]:
        key = (record.source, record.source_identifier)
        issues = list(validate_record(record, now=now))
        if key in self.records:
            issues.append(
                ValidationIssue("duplicate_identifier", "source_identifier already exists")
            )
        if issues:
            self.quarantine.append(
                QuarantinedRecord(
                    source=record.source,
                    source_identifier=record.source_identifier,
                    reason=tuple(issues),
                    raw=(
                        record.raw_payload
                        if record.raw_payload is not None
                        else record.raw_reference
                    ),
                    quarantined_at=now or datetime.now(UTC),
                )
            )
            return False, tuple(issues)
        normalized = normalize_record_payload(record)
        current = (now or datetime.now(UTC)).astimezone(UTC)
        normalized = normalized.model_copy(
            update={
                "freshness": evaluate_freshness(
                    normalized.observed_at, now=current, domain=normalized.domain.value
                )
            }
        )
        self.records[key] = normalized
        return True, ()

    def ingest(self, connector: SourceConnector, *, now: datetime | None = None) -> IngestionResult:
        accepted = 0
        quarantined_before = len(self.quarantine)
        for item in connector.fetch():
            if isinstance(item, SourceRecord):
                record = item
            else:
                try:
                    envelope = SourceRecord[Any].model_validate(item)
                    payload_type = _PAYLOAD_TYPES[envelope.domain]
                    typed_payload = payload_type.model_validate(envelope.normalized_payload)
                    record = SourceRecord[Any].model_validate(
                        {**envelope.model_dump(), "normalized_payload": typed_payload}
                    )
                except ValidationError as exc:
                    issue = ValidationIssue("invalid_envelope", str(exc))
                    self.quarantine.append(
                        QuarantinedRecord(
                            reason=(issue,), raw=item, quarantined_at=now or datetime.now(UTC)
                        )
                    )
                    continue
                except KeyError as exc:
                    issue = ValidationIssue("unsupported_domain", f"unsupported domain: {exc}")
                    self.quarantine.append(
                        QuarantinedRecord(
                            reason=(issue,), raw=item, quarantined_at=now or datetime.now(UTC)
                        )
                    )
                    continue
            ok, _ = self.register(record, now=now)
            accepted += int(ok)
        quarantined = self.quarantine[quarantined_before:]
        return IngestionResult(
            accepted=accepted,
            quarantined=len(quarantined),
            quarantined_records=tuple(quarantined),
        )

    def health(self) -> list[dict[str, Any]]:
        latest: dict[str, SourceRecord[Any]] = {}
        for record in self.records.values():
            previous = latest.get(record.source)
            if previous is None or record.ingested_at > previous.ingested_at:
                latest[record.source] = record
        return [
            {
                "source": source,
                "latest_update": record.ingested_at,
                "latest_observed_at": record.observed_at,
                "status": record.status,
                "quality": record.quality_score,
                "quality_score": record.quality_score,
                "freshness": record.freshness,
                "records": sum(item.source == source for item in self.records.values()),
            }
            for source, record in sorted(latest.items())
        ]


class DataPipeline:
    """Small façade that keeps route code independent from connectors."""

    def __init__(self, registry: SourceRegistry | None = None) -> None:
        self.registry = registry or SourceRegistry()

    def ingest(self, connector: SourceConnector, *, now: datetime | None = None) -> IngestionResult:
        return self.registry.ingest(connector, now=now)


# Process-local default for the read-only health surface. Applications can
# construct and inject a persistent registry when storage is introduced.
registry = SourceRegistry()


_PAYLOAD_TYPES: dict[DataDomain, type[PayloadModel]] = {
    DataDomain.FREIGHT_MARKET: FreightMarketPayload,
    DataDomain.AIS_VESSEL: AISVesselPayload,
    DataDomain.PORT: PortPayload,
    DataDomain.BERTH: BerthPayload,
    DataDomain.WEATHER: WeatherPayload,
    DataDomain.FUEL: FuelPayload,
    DataDomain.FX: FXPayload,
    DataDomain.INVENTORY: InventoryPayload,
    DataDomain.ROUTE_REFERENCE: RouteReferencePayload,
    DataDomain.NEWS_GEOPOLITICAL: NewsGeopoliticalPayload,
}
