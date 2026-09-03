# Data Schemas

Phase 3 defines one `SourceRecord[T]` envelope for all external, file, mock and
synthetic data. `T` is a typed Pydantic payload for one of:
`freight_market`, `ais_vessel`, `port`, `berth`, `weather`, `fuel`, `fx`,
`inventory`, `route_reference`, or `news_geopolitical`.

Each envelope contains `source`, `source_identifier`, timezone-aware
`observed_at` and `ingested_at`, a `quality_score` in `[0, 1]`, `freshness`,
`status` (`LIVE`, `DELAYED`, `ESTIMATED`, `SYNTHETIC`, `DEMO`), raw payload or
reference, normalized payload, `schema_version`, and lineage metadata
(`ingestion_job_id`, `transformation_version`, connector and parent IDs).
Payload models enforce coordinates, positive rates/prices, non-negative
quantities, and domain-specific identifiers.

Phase 4 also defines `SyntheticRecord` for scenario-only domains that do not yet
have a persistence/source payload contract (congestion, voyages, and contract
alternatives). It carries a stable record ID, scenario, geography, observation
time, payload, and explicit `SYNTHETIC` or `DEMO` status.
