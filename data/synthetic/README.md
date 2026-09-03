# Synthetic Data

This directory contains optional JSON artifacts generated for local development.
They are reproducible for the same seed, scenario, date range, region, and
quantity. Records use `SYNTHETIC` status and have no provider/network dependency.

```bash
PYTHONPATH=backend python scripts/generate_ais.py
PYTHONPATH=backend python scripts/generate_market.py
```
