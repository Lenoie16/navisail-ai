import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_demo_runner_is_repeatable_and_preserves_baseline() -> None:
    command = [sys.executable, str(ROOT / "scripts" / "run_demo.py"), "--json"]
    first = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    second = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    result = json.loads(first.stdout)
    assert result == json.loads(second.stdout)
    assert result["source_status"] == "DEMO"
    assert result["shock"]["scenario_congestion_days"] == result["shock"]["baseline_congestion_days"] + 5
    assert result["stages"][-1]["details"]["side_effects"] is False
    assert {stage["name"] for stage in result["stages"]} == {
        "shipment", "maritime_state", "forecast", "vessel_candidates",
        "port_berth_compatibility", "congestion", "landed_cost", "charter_timing",
        "contract_comparison", "monte_carlo_risk", "digital_twin", "inventory_impact",
        "recommendation", "explainability", "copilot", "human_approval", "execution_audit",
    }
