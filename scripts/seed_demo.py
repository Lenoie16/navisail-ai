"""Write the canonical deterministic NAVISAIL demo package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.seeds import seed_reference_data
from app.db.session import SessionLocal
from app.synthetic import generate_demo_scenario


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=26006)
    parser.add_argument("--output", type=Path, default=Path("data/demo/scenario.json"))
    parser.add_argument(
        "--with-database",
        action="store_true",
        help="also seed the Phase 2 reference rows using DATABASE_URL",
    )
    args = parser.parse_args()
    scenario = generate_demo_scenario(seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(scenario, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.with_database:
        with SessionLocal() as session:
            seed_reference_data(session)
    print(f"Wrote DEMO scenario to {args.output}")


if __name__ == "__main__":
    main()
