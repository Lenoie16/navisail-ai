# NAVISAIL AI

NAVISAIL AI is a modular-monolith foundation for maritime procurement, chartering, and logistics
decision intelligence. The product loop is **PREDICT → SIMULATE → OPTIMIZE → DECIDE**.

## Local setup

Requirements: Python 3.12+, Node.js 22+, pnpm 9+, and Docker Compose.

```bash
cp .env.example .env
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pnpm install
```

If you prefer a requirements-based Python setup, install the equivalent runtime and
development dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Data platform foundation (Phase 3)

Phase 3 defines typed source envelopes for freight, AIS, ports, berths, weather, fuel,
FX, inventory, routes, and geopolitical signals. Mock, file, and deterministic synthetic
connectors share validation, normalization, freshness, quarantine, and lineage interfaces.
Source status is preserved explicitly and is never inferred as live.

Read-only source health is available at:

```text
GET /api/v1/data-health
GET /api/v1/data-health/sources
```

See the [source catalog](docs/data/source-catalog.md), [quality rules](docs/data/quality.md),
[freshness policies](docs/data/freshness.md), [lineage](docs/data/lineage.md), and
[schemas](docs/data/schemas.md) for the Phase 3 contracts.

### Phase 5 canonical maritime state

The `MaritimeStateVector` builder assembles normalized source records into one
versioned, decision-session-scoped state snapshot. Snapshot creation, retrieval,
session listing, and comparison are available under `/api/v1/maritime-state`.
See [MaritimeStateVector](docs/architecture/maritime-state.md).

### Phase 4 deterministic synthetic and demo data

`app.synthetic` provides seeded generators for vessels and AIS trajectories,
ports/berths, freight, fuel, FX, congestion, weather, inventory, voyages,
contract alternatives, and named market shocks. The same inputs always produce
the same JSON. The canonical `au-steel-east-india` scenario is a 150,000 MT
Australia-origin movement to the Bokaro steel plant and is explicitly marked
`DEMO`; generated development records are marked `SYNTHETIC`. No generator
represents a live feed and this phase does not forecast or optimize.

```bash
PYTHONPATH=backend python scripts/seed_demo.py
PYTHONPATH=backend python scripts/generate_ais.py
PYTHONPATH=backend python scripts/generate_market.py
python scripts/reset_demo.py
```

Start dependencies with `docker compose up postgres redis`, then run the applications independently:

```bash
make backend-dev     # http://localhost:8000
make frontend-dev    # http://localhost:3000
```

Or start the complete development environment with `make up`.

For a production-like local deployment with immutable service images, an
explicit migration step, readiness checks, and a worker process, use:

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build
```

See [deployment operations](docs/architecture/deployment.md) for startup,
environment, rollback, backup, and recovery guidance.

## Service endpoints

- Backend health: `GET http://localhost:8000/api/v1/health`
- Backend version: `GET http://localhost:8000/api/v1/version`
- OpenAPI UI: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`
- PostgreSQL/PostGIS: `localhost:5432`
- Redis: `localhost:6379`

## Quality gates

```bash
make test
make lint
make format
make typecheck
make build
```

The backend uses Ruff, strict mypy, pytest, and an 80% coverage floor. The frontend uses ESLint,
Prettier, TypeScript, Vitest, and a production Next.js build.

## Configuration

Copy [.env.example](.env.example) to `.env`. The file documents application, database, Redis, CORS,
logging, demo-mode, timezone, and frontend API settings. Secrets belong only in local environment
files or the deployment secret store; never commit them.

### Data Docked live mode

Data Docked is an optional backend-only maritime provider. It is never called
by the browser or directly by Copilot. Keep the deterministic demo independent
of it:

```bash
NAVISAIL_MODE=DEMO
DATADOCKED_ENABLED=false
```

For an explicitly configured live environment, provide the API key through the
deployment secret store and set `NAVISAIL_MODE=LIVE` and
`DATADOCKED_ENABLED=true`. The backend exposes only NAVISAIL-owned normalized
surfaces:

```text
GET  /api/v1/data-sources/datadocked/health
POST /api/v1/data-sources/datadocked/vessels/location
GET  /api/v1/runtime/data-status
```

See [Data Docked integration](docs/data/datadocked-integration.md) for cache,
freshness, credit, rate-limit, fallback, security, and testing behavior.

## Architecture

The repository is intentionally a modular monolith. Domain engines are isolated behind typed boundaries
so they can be extracted later without prematurely introducing distributed services. See:

- [System architecture](docs/architecture/system-architecture.md)
- [Domain boundaries](docs/architecture/domain-boundaries.md)
- [Data flow](docs/architecture/data-flow.md)
- [Testing strategy](docs/testing/strategy.md)

## Persistence foundation (Phase 2)

Phase 2 adds SQLAlchemy 2 typed models for the maritime domain, PostgreSQL/PostGIS support,
SQLite-compatible tests, Alembic migrations, deterministic reference seeds, and CRUD APIs for
shipments, vessels, ports, berths, and plants. Intelligence calculations and unfinished
forecasting/optimization endpoints remain intentionally unexposed.

Run the initial schema migration with:

```bash
DATABASE_URL=postgresql+psycopg://navisail:navisail@localhost:5432/navisail alembic upgrade head
```
