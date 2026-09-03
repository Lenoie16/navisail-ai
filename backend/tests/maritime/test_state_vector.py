from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.data.contracts import AISVesselPayload, AISVesselRecord, Lineage, SourceStatus
from app.data.freshness import FreshnessInfo, FreshnessState
from app.maritime.state_vector import (
    StateComponent,
    build_state_vector,
    diff_state_vectors,
)


def _record(observed_at: datetime) -> AISVesselRecord:
    job = UUID("00000000-0000-0000-0000-000000000010")
    return AISVesselRecord(
        source="synthetic-engine",
        source_identifier="ais-1",
        observed_at=observed_at,
        ingested_at=observed_at,
        quality_score=0.9,
        status=SourceStatus.SYNTHETIC,
        raw_payload={"vessel_id": "v-1"},
        normalized_payload=AISVesselPayload(
            vessel_id="v-1", latitude=20, longitude=80, speed_knots=12
        ),
        schema_version="1.0",
        ingestion_job_id=job,
        transformation_version="synthetic-v1",
        lineage=Lineage(
            ingestion_job_id=job,
            transformation_version="synthetic-v1",
            connector_name="synthetic",
        ),
    )


def test_state_assembly_is_reproducible_and_preserves_metadata() -> None:
    session = UUID("00000000-0000-0000-0000-000000000020")
    generated = datetime(2025, 1, 2, tzinfo=UTC)
    first = build_state_vector(
        {"ais": _record(generated)},
        decision_session_id=session,
        generated_at=generated,
        effective_at=generated,
    )
    second = build_state_vector(
        {"ais": _record(generated)},
        decision_session_id=session,
        generated_at=generated,
        effective_at=generated,
    )
    assert first == second
    assert first.components["ais"].status == "SYNTHETIC"
    assert first.components["ais"].source == "synthetic-engine"


def test_state_diff_identifies_changed_and_stale_components() -> None:
    session = UUID("00000000-0000-0000-0000-000000000020")
    now = datetime(2025, 1, 2, tzinfo=UTC)
    before = build_state_vector(
        {"ais": _record(now)},
        decision_session_id=session,
        generated_at=now,
    )
    stale = StateComponent(
        timestamp=now - timedelta(days=2),
        source="old-feed",
        quality=0.4,
        freshness=FreshnessInfo(
            state=FreshnessState.STALE,
            age_seconds=172800,
            threshold_seconds=900,
            evaluated_at=now,
        ),
        status="DELAYED",
        confidence=0.4,
        data={"vessel_id": "v-1"},
    )
    after = build_state_vector(
        {"ais": stale, "weather": stale},
        decision_session_id=session,
        version=2,
        generated_at=now,
    )
    result = diff_state_vectors(before, after)
    assert result.added == ["weather"]
    assert result.changed == ["ais"]
    assert result.stale == ["ais", "weather"]
    assert result.material_changes == ["ais", "weather"]
