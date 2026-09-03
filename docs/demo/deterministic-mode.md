# Deterministic Mode

`scripts/run_demo.py` runs in-process and offline with seed `26006`, clock
`2025-01-06T09:00:00Z`, and the `au-steel-east-india` fixture. It does not
require Redis, a database service, an HTTP server, or live provider feeds.
Repeated JSON runs produce the same determinism hash. All records are labeled
`DEMO` or `SYNTHETIC`; demo approval/execution records set
`side_effects: false`.
