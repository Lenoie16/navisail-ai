"""Generate deterministic AIS JSON for local development."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.synthetic import generate_ais_positions, records_to_jsonable  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=26006)
    parser.add_argument("--scenario-id", default="synthetic")
    parser.add_argument("--start-date", default="2025-01-01")
    parser.add_argument("--end-date", default="2025-01-07")
    parser.add_argument("--region", default="Australia-East Coast India")
    parser.add_argument("--vessels", type=int, default=6)
    parser.add_argument("--points-per-vessel", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic/ais.json"))
    args = parser.parse_args()
    records = generate_ais_positions(
        seed=args.seed,
        scenario_id=args.scenario_id,
        start_date=date.fromisoformat(args.start_date),
        end_date=date.fromisoformat(args.end_date),
        geographic_region=args.region,
        quantity=args.vessels,
        points_per_vessel=args.points_per_vessel,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(records_to_jsonable(records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(records)} synthetic AIS records to {args.output}")


if __name__ == "__main__":
    main()
