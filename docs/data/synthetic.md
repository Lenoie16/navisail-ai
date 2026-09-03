# Deterministic synthetic data (Phase 4)

The `app.synthetic` package supplies dependency-free, seeded fixtures for local
development and the SIH demo. Generators accept a seed, scenario identifier,
date range, geographic region, and relevant quantity/volume arguments. Stable
UUID5 identifiers and fixed timestamps make serialized output reproducible.

Domains include vessels, AIS positions, ports, berths, freight observations,
fuel, FX, weather, inventory, congestion, voyages, contract alternatives, and
market shocks. Ports, berths, AIS, freight, fuel, FX, weather, and inventory use
the Phase 3 Pydantic source envelopes. Other domains use `SyntheticRecord` until
their source payload contracts are introduced.

`SYNTHETIC` and `DEMO` statuses are preserved on every record. The canonical demo
is `generate_demo_scenario()` and describes a 150,000 MT Australia-to-Bokaro
steel plant movement with candidate ports, vessels, contracts, congestion, and
inventory exposure. `apply_shock` returns a deep-copied, modified fixture; it
never mutates the source list.

Named shocks are port outage, congestion +5 days, freight spike, cyclone, fuel
spike, vessel failure, and severe congestion. They are deterministic scenario
inputs, not forecasts or optimization intelligence.
