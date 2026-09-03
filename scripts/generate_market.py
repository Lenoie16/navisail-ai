"""Generate deterministic market JSON for local development."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.synthetic import (  # noqa: E402
    generate_congestion,
    generate_contract_alternatives,
    generate_freight_observations,
    generate_fuel,
    generate_fx,
    generate_market_shocks,
    records_to_jsonable,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=26006)
    parser.add_argument("--scenario-id", default="synthetic")
    parser.add_argument("--start-date", default="2025-01-01")
    parser.add_argument("--end-date", default="2025-01-07")
    parser.add_argument("--region", default="Australia-East Coast India")
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/market.json"))
    args = parser.parse_args()
    common = {
        "seed": args.seed,
        "scenario_id": args.scenario_id,
        "start_date": date.fromisoformat(args.start_date),
        "end_date": date.fromisoformat(args.end_date),
        "geographic_region": args.region,
    }
    bundle = {
        "freight": records_to_jsonable(generate_freight_observations(**common)),
        "fuel": records_to_jsonable(generate_fuel(**common)),
        "fx": records_to_jsonable(generate_fx(**common)),
        "congestion": records_to_jsonable(generate_congestion(**common)),
        "contract_alternatives": records_to_jsonable(generate_contract_alternatives(**common)),
        "market_shocks": [
            shock.model_dump(mode="json") for shock in generate_market_shocks(**common)
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote synthetic market data to {args.output}")


if __name__ == "__main__":
    main()
