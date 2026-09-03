# Freshness

Freshness is evaluated deterministically from `observed_at` and an explicit
UTC policy threshold. The result contains `FRESH`, `STALE`, or `UNKNOWN`,
`age_seconds`, `threshold_seconds`, and `evaluated_at`. Default thresholds are
short for AIS and weather and longer for reference data; callers can provide a
domain-specific threshold.

Normalization never changes source `status`. A stale record remains
`LIVE`/`DELAYED`/`ESTIMATED`/`SYNTHETIC`/`DEMO`; freshness is an independent
operational signal.
