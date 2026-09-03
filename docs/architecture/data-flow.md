# Data Flow

The backend follows a thin API → service/repository → SQLAlchemy session flow:

1. FastAPI validates request payloads with Pydantic schemas and obtains a request-scoped
   `Session` from `app.dependencies.get_db`.
2. CRUD services/repositories persist only the supported operational resources: shipments,
   vessels, ports, berths, and plants. Repositories commit, refresh, and translate integrity
   failures into HTTP 409 responses.
3. SQLAlchemy maps UUID identities, UTC timestamps, validated enums, foreign keys, checks, and
   indexes to PostgreSQL/PostGIS. Geospatial values cross the boundary as WKT-compatible
   strings; the PostgreSQL dialect uses geography columns.
4. Responses are serialized from ORM instances through `from_attributes` Pydantic read models.
   Unfinished forecasting, optimization, recommendation, execution, and audit routers are not
   registered, so no intelligence behavior is exposed accidentally.

Schema lifecycle is managed by Alembic. The initial migration enables PostGIS when running
against PostgreSQL and remains executable against SQLite for tests. Deterministic reference
seeds are explicit application data, not hidden ORM side effects.
## Canonical maritime state

Normalized source records are assembled by the MaritimeStateVector builder into
one versioned snapshot shared by downstream engines. Each component retains its
timestamp, source, quality, freshness, status, confidence, and normalized data.
Snapshots are reproducible for fixed inputs and can be compared for added,
changed, removed, and stale components. Downstream engines must consume this
contract rather than reconstructing independent maritime state.
