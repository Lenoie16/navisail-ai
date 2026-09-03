"""Run the offline, deterministic NAVISAIL SIH showcase."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.risk.monte_carlo import SimulationAlternative, monte_carlo_engine
from app.risk.scenarios import DEFAULT_SCENARIOS
from app.synthetic import (
    ShockType,
    apply_shock,
    generate_congestion,
    generate_demo_scenario,
    generate_market_shocks,
)

SEED = 26006
CLOCK = datetime(2025, 1, 6, 9, 0, tzinfo=UTC)
STAGES = (
    "shipment", "maritime_state", "forecast", "vessel_candidates",
    "port_berth_compatibility", "congestion", "landed_cost", "charter_timing",
    "contract_comparison", "monte_carlo_risk", "digital_twin", "inventory_impact",
    "recommendation", "explainability", "copilot", "human_approval", "execution_audit",
)


def _stage(name: str, status: str = "completed", **details: Any) -> dict[str, Any]:
    return {"name": name, "status": status, "source_status": "DEMO", "details": details}


def _risk(scenario: Any) -> list[dict[str, Any]]:
    alternatives = (
        SimulationAlternative(alternative_id="spot-paradip", base_cost=34.8 * 150_000,
                              base_delay_hours=12, cost_threshold=6_000_000,
                              freight_exposure=0.8),
        SimulationAlternative(alternative_id="coa-dhamra", base_cost=31.9 * 150_000,
                              base_delay_hours=20, cost_threshold=6_000_000,
                              freight_exposure=0.5),
    )
    return [item.model_dump(mode="json") for item in monte_carlo_engine.simulate(
        alternatives, scenario=scenario, simulations=2_000, seed=SEED
    )]


def build_demo() -> dict[str, Any]:
    baseline = generate_demo_scenario(seed=SEED)
    congestion_records = generate_congestion(
        seed=SEED, scenario_id=baseline["scenario_id"], demo=True
    )
    shock = next(item for item in generate_market_shocks(scenario_id=baseline["scenario_id"])
                 if item.shock_type is ShockType.CONGESTION_PLUS_5_DAYS)
    target_before = next(item for item in congestion_records if item.payload["port_id"] == shock.target)
    shocked = apply_shock(congestion_records, shock)
    target_after = next(item for item in shocked if item.payload["port_id"] == shock.target)
    before = target_before.payload["congestion_days"]
    after = target_after.payload["congestion_days"]
    volatile = DEFAULT_SCENARIOS["volatile"].model_copy(
        update={"name": "congestion_plus_5_days", "waiting_hours": 120}
    )
    result = {
        "demo": True,
        "source_status": "DEMO",
        "scenario_id": baseline["scenario_id"],
        "seed": SEED,
        "clock": CLOCK.isoformat(),
        "live_feeds": False,
        "baseline": baseline,
        "shock": {
            "id": shock.shock_id,
            "type": shock.shock_type.value,
            "target": shock.target,
            "baseline_congestion_days": before,
            "scenario_congestion_days": after,
            "recommendation_change": "unavailable: critical recommendation inputs are incomplete",
            "risk_baseline": _risk(DEFAULT_SCENARIOS["normal"]),
            "risk_scenario": _risk(volatile),
        },
        "stages": [
            _stage("shipment", volume_tonnes=baseline["cargo"]["volume_tonnes"]),
            _stage("maritime_state", records=len(baseline["ais_positions"])),
            _stage("forecast", "unavailable", reason="no authoritative forecast window"),
            _stage("vessel_candidates", count=len(baseline["vessels"])),
            _stage("port_berth_compatibility", ports=len(baseline["ports"]), berths=len(baseline["berths"])),
            _stage("congestion", baseline_days=before, scenario_days=after),
            _stage("landed_cost", "unavailable", reason="no fabricated cost result"),
            _stage("charter_timing", "unavailable", reason="requires authoritative booking candidates"),
            _stage("contract_comparison", alternatives=len(baseline["contract_alternatives"])),
            _stage("monte_carlo_risk"),
            _stage("digital_twin", "unavailable", reason="requires assembled state vector"),
            _stage("inventory_impact", committed_tonnes=baseline["inventory_exposure"]["committed_volume_tonnes"]),
            _stage("recommendation", "unavailable", reason="critical inputs incomplete"),
            _stage("explainability", "unavailable", reason="recommendation unavailable"),
            _stage("copilot", "unavailable", reason="no authoritative context"),
            _stage("human_approval", "demo_only", side_effects=False),
            _stage("execution_audit", "demo_only", side_effects=False),
        ],
    }
    result["determinism_hash"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit stable JSON only")
    args = parser.parse_args()
    result = build_demo()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("NAVISAIL SIH DEMO | DEMO/SYNTHETIC DATA | offline deterministic mode")
        print(f"Scenario: {result['scenario_id']} | seed={SEED} | clock={result['clock']}")
        for stage in result["stages"]:
            print(f"- {stage['name']}: {stage['status']}")
        print(f"Shock: Paradip congestion {result['shock']['baseline_congestion_days']} -> "
              f"{result['shock']['scenario_congestion_days']} days")
        print(f"Determinism hash: {result['determinism_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
