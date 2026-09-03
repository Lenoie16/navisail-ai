"""Map provider responses into NAVISAIL source contracts."""

from datetime import UTC, datetime
from uuid import uuid4

from app.data.contracts import AISVesselPayload, AISVesselRecord, Lineage, SourceStatus
from app.data.datadocked_schemas import VesselLocationResponse
from app.data.freshness import evaluate_freshness


def map_vessel_location(
    payload: dict[str, object],
    *,
    received_at: datetime | None = None,
    connector_name: str = "datadocked",
) -> AISVesselRecord:
    received = (received_at or datetime.now(UTC)).astimezone(UTC)
    response = VesselLocationResponse.model_validate(payload)
    identifier = response.imo or response.mmsi
    if not identifier:
        raise ValueError("Data Docked vessel response has no IMO or MMSI")
    record_id = response.imo or response.mmsi or identifier
    job_id = uuid4()
    return AISVesselRecord(
        source="DATADOCKED",
        source_identifier=record_id,
        observed_at=response.observed_at,
        ingested_at=received,
        quality_score=1.0 if response.imo else 0.8,
        freshness=evaluate_freshness(response.observed_at, now=received, domain="ais_vessel"),
        status=(
            SourceStatus.LIVE
            if evaluate_freshness(
                response.observed_at, now=received, domain="ais_vessel"
            ).state.value
            == "FRESH"
            else SourceStatus.DELAYED
        ),
        raw_payload=payload,
        normalized_payload=AISVesselPayload(
            vessel_id=identifier,
            latitude=response.latitude,
            longitude=response.longitude,
            speed_knots=response.speed or 0,
            heading_degrees=response.heading if response.heading is not None else response.course,
        ),
        schema_version="datadocked-v1",
        ingestion_job_id=job_id,
        transformation_version="datadocked-normalizer-v1",
        lineage=Lineage(
            ingestion_job_id=job_id,
            transformation_version="datadocked-normalizer-v1",
            connector_name=connector_name,
        ),
    )
