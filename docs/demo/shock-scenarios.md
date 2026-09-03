# Shock Scenarios

The engine exposes deterministic shock definitions for:

- port outage
- congestion increase of exactly five days
- freight spike
- cyclone disruption
- fuel-price spike
- vessel failure
- severe congestion

Use `generate_market_shocks()` to list definitions and `apply_shock(records,
definition)` to transform a copied fixture. Shock application never mutates
the baseline records and preserves `SYNTHETIC` or `DEMO` status.
