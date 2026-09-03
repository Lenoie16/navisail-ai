# NAVISAIL AI 0.1.0-rc.1

**Release candidate date:** 2026-09-03  
**Release intent:** Stable, deterministic SIH demonstration and auditable
decision-intelligence foundation.

## Build and test status

| Check | Result |
| --- | --- |
| Python dependency check (`pip check`) | Pass |
| Python compile/import check | Pass |
| Frozen pnpm installation | Pass |
| Production Compose syntax | Pass with required check credentials |
| Backend full suite | 89 passed |
| Release workflow smoke tests | 19 passed |
| Deterministic demo repeatability | Pass; two JSON outputs identical |
| Frontend typecheck, lint, format, Vitest | Pass; 15 frontend tests |
| Frontend production build | Pass |

The backend suite emits one known Starlette/httpx deprecation warning. Ruff and
strict mypy findings remain documented pre-existing issues in the
[Phase 40 report](../testing/phase-40-report.md).

## Startup

Development:

```bash
cp .env.example .env
make up
```

Production-like local topology:

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build
```

The production-like topology requires `POSTGRES_PASSWORD` and `AUTH_TOKEN`.
It defaults to the internal `postgres` service hostname. Set
`COMPOSE_DATABASE_URL` only for an intentional external database. Keep secrets
in the environment or deployment secret store.
Run migrations before application traffic:

```bash
docker compose -f docker-compose.prod.yml --env-file .env run --rm migrate
```

## SIH demo

```bash
PYTHONPATH=backend .venv/bin/python scripts/run_demo.py
PYTHONPATH=backend .venv/bin/python scripts/run_demo.py --json
```

Use the sequence in [judging-flow.md](../sih/judging-flow.md), including the
Paradip `congestion_plus_5_days` shock. Demo approval and execution are
explicitly side-effect-free.

## Feature and limitation summary

The implemented and tested domain matrix is maintained in
[requirement-traceability.md](../sih/requirement-traceability.md). The release
includes deterministic foundations for maritime state, forecasting,
compatibility, congestion, landed cost, optimization, Charter Now/Wait,
contracts, risk, digital twin, inventory, recommendations, explainability,
Copilot, agents, approval, execution, audit, MLOps, RBAC, and realtime SSE.

This release candidate does **not** claim connected live AIS/market/weather/ERP
or TMS providers, enterprise identity integration, durable distributed job
queue semantics, production cloud provisioning, automated Playwright journeys,
or machine-independent performance SLAs. Synthetic and demo data are labeled
and unavailable authoritative values remain unavailable.

## Release decision

**SIH demonstration:** Ready.  
**Production deployment:** Not yet; close the documented integration,
durability, quality-gate, browser-E2E, and performance evidence gaps first.
