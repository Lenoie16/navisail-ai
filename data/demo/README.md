# Demo Data

`scripts/seed_demo.py` writes `scenario.json` here. The canonical fixture is a
150,000 MT Australia-origin steelmaking-coal movement to the Bokaro steel plant
through East Coast India ports. Every record is marked `DEMO`; it is not a live
market or AIS feed.

```bash
PYTHONPATH=backend python scripts/seed_demo.py
# Add --with-database when DATABASE_URL points to a running database.
python scripts/reset_demo.py
```
