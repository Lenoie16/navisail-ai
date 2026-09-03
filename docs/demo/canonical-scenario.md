# Canonical Scenario

The deterministic `au-steel-east-india` scenario represents a 150,000 MT
Australia-origin bulk shipment to the Bokaro steel plant through Paradip and
Dhamra. It includes six vessel candidates, AIS trajectories, port and berth
records, freight and bunker observations, FX, congestion, weather, inventory
exposure, voyage options, and spot/COA/time-charter/hybrid alternatives.

Generate it with:

```bash
PYTHONPATH=backend python scripts/seed_demo.py
```

The resulting records are labeled `DEMO`, use a fixed default seed, and contain
no live-provider claims.
