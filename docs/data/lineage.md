# Data Lineage

Every accepted record carries a UUID `ingestion_job_id`, immutable
`transformation_version`, connector name, and optional parent record IDs in a
typed `Lineage` object. The IDs are also present at envelope level for easy
indexing and are checked for consistency.

`normalize_payload` trims strings and recursively sorts mapping keys. It is
deterministic and repeatable, and does not alter status, timestamps, source
identity, or raw payload. Provider integrations and persistence are outside
this phase; the registry is the replaceable orchestration boundary.
