"""Determinism and shock tests for Phase 4 synthetic fixtures."""

from __future__ import annotations

import hashlib
import json

from app.data.contracts import SourceStatus
from app.synthetic import (
    ShockType,
    apply_shock,
    generate_congestion,
    generate_demo_scenario,
    generate_market_shocks,
    generate_vessels,
    records_to_jsonable,
)


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_canonical_demo_is_repeatable_and_explicitly_demo() -> None:
    first = generate_demo_scenario()
    second = generate_demo_scenario()
    assert _digest(first) == _digest(second)
    assert first["source_status"] == "DEMO"
    assert first["cargo"]["volume_tonnes"] == 150000
    assert len(first["vessels"]) == 6
    assert len(first["ais_positions"]) == 48
    assert all(record["status"] == SourceStatus.DEMO.value for record in first["ports"])


def test_named_congestion_shock_adds_exactly_five_days_to_target() -> None:
    records = generate_congestion()
    shock = next(
        definition
        for definition in generate_market_shocks()
        if definition.shock_type is ShockType.CONGESTION_PLUS_5_DAYS
    )
    changed = apply_shock(records, shock)
    before = {
        record["payload"]["port_id"]: record["payload"]["congestion_days"] for record in records
    }
    after = {
        record["payload"]["port_id"]: record["payload"]["congestion_days"] for record in changed
    }
    assert after["INPRD"] == before["INPRD"] + 5
    assert after["INDBD"] == before["INDBD"]
    assert records[0]["payload"]["congestion_days"] != changed[0]["payload"]["congestion_days"]


def test_synthetic_envelopes_are_never_live() -> None:
    records = records_to_jsonable(generate_congestion())
    assert records
    assert all(record["source_status"] in {"SYNTHETIC", "DEMO"} for record in records)


def test_vessel_failure_marks_the_first_candidate_unavailable() -> None:
    records = generate_vessels()
    shock = next(
        definition
        for definition in generate_market_shocks()
        if definition.shock_type is ShockType.VESSEL_FAILURE
    )
    changed = apply_shock(records, shock)
    assert changed[0].payload["status"] == "failed"
    assert changed[0].payload["available"] is False
    assert records[0].payload["status"] == "active"
