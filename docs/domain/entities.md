# Persistence entities

The Phase 2 persistence layer is a typed SQLAlchemy 2 model with UUID primary keys and
UTC-aware timestamps. PostgreSQL deployments use PostGIS geography (WGS84): ports,
plants, origins and vessel positions are points, while routes store line geometry.
SQLite is supported for deterministic tests through portable WKT storage.

## Operational entities

- **Shipment** references a commodity, plant, origin, and optional origin/destination ports.
  Positive tonnage and a valid planned schedule are enforced by database checks.
- **Vessel** stores IMO identity, type, capacity/draft and status. **VesselPosition** records
  timestamped geospatial observations with indexed vessel/time and spatial lookups.
- **Port** uses a unique UN/LOCODE and owns **Berth** records. Berth codes are unique per port
  and draft is positive when supplied.

## Planning and governance entities

**Route** and **Voyage** model planned movement; **Contract** models counterparty validity;
**Inventory** tracks non-negative plant/commodity balances; and **DecisionSession**,
**MaritimeStateSnapshot**, **Recommendation**, **Approval**, **Execution**, and **AuditRecord**
provide an auditable decision lifecycle. Intelligence calculations are deliberately outside
the ORM and API CRUD boundary.

Enums are persisted as named PostgreSQL enums (validated strings in SQLite), and foreign keys
use explicit delete behavior. Alembic revision `0001_initial` creates the complete schema.
`app.db.seeds.seed_reference_data` provides stable demo reference identifiers.
