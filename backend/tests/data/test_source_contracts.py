from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from app.data.connectors import FileConnector
from app.data.contracts import (
    AISVesselPayload,
    AISVesselRecord,
    Lineage,
    SourceStatus,
)
from app.data.freshness import FreshnessState, evaluate_freshness
from app.data.normalize import normalize_record_payload
from app.data.pipeline import SourceRegistry
from app.data.validation import validate_record
from pydantic import ValidationError


def make_record(
    *, identifier: str = "ais-1", status: SourceStatus = SourceStatus.DELAYED
) -> AISVesselRecord:
    job_id = uuid4()
    now = datetime.now(UTC)
    return AISVesselRecord(
        source="test-ais",
        source_identifier=identifier,
        observed_at=now - timedelta(minutes=2),
        ingested_at=now,
        quality_score=0.8,
        status=status,
        raw_payload={"longitude": 4.2, "latitude": 51.9},
        normalized_payload=AISVesselPayload(
            vessel_id="v-1", latitude=51.9, longitude=4.2, speed_knots=12
        ),
        schema_version="1.0",
        ingestion_job_id=job_id,
        transformation_version="normalizer-1",
        lineage=Lineage(
            ingestion_job_id=job_id,
            transformation_version="normalizer-1",
            connector_name="mock",
        ),
    )


def test_invalid_coordinates_are_rejected() -> None:
    with pytest.raises(ValidationError):
        AISVesselPayload(vessel_id="v-1", latitude=95, longitude=4)


def test_registry_quarantines_duplicate_identifier_and_preserves_status() -> None:
    registry = SourceRegistry()
    first = make_record()
    assert registry.register(first)[0]
    assert not registry.register(make_record())[0]
    assert registry.quarantine[-1].reason[0].code == "duplicate_identifier"
    accepted = registry.records[("test-ais", "ais-1")]
    assert accepted.status is SourceStatus.DELAYED


def test_normalization_is_repeatable_and_freshness_is_explicit() -> None:
    record = make_record(status=SourceStatus.SYNTHETIC)
    once = normalize_record_payload(record)
    twice = normalize_record_payload(once)
    assert once.normalized_payload.model_dump() == twice.normalized_payload.model_dump()
    freshness = evaluate_freshness(
        record.observed_at, now=record.ingested_at, threshold_seconds=60, domain="ais_vessel"
    )
    assert freshness.state is FreshnessState.STALE


def test_stale_and_inconsistent_units_are_reported() -> None:
    record = make_record()
    stale = validate_record(
        record,
        now=record.ingested_at + timedelta(hours=1),
        stale_after_seconds=60,
    )
    assert any(issue.code == "stale_data" for issue in stale)

    payload = AISVesselPayload.model_validate(
        {
            "vessel_id": "v-1",
            "latitude": 51.9,
            "longitude": 4.2,
            "unit": "tonnes",
            "speed_unit": "knots",
        }
    )
    mixed = record.model_copy(update={"normalized_payload": payload})
    issues = validate_record(mixed)
    assert any(issue.code == "inconsistent_unit" for issue in issues)


def test_file_connector_ingests_domain_typed_envelopes(tmp_path) -> None:
    record = make_record()
    path = tmp_path / "records.json"
    path.write_text(record.model_dump_json(), encoding="utf-8")

    registry = SourceRegistry()
    result = registry.ingest(FileConnector(path))

    assert result.accepted == 1
    accepted = registry.records[("test-ais", "ais-1")]
    assert isinstance(accepted.normalized_payload, AISVesselPayload)
