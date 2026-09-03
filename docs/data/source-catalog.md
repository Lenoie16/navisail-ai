# Source Catalog

| Domain | Contract payload | Typical freshness policy |
| --- | --- | --- |
| Freight market | route, vessel class, rate, currency, unit | 24 hours |
| AIS/vessel | vessel, coordinate, speed, heading | 15 minutes |
| Port | port, name, country, coordinate | 7 days |
| Berth | berth, port, draft, availability | 24 hours |
| Weather | location, coordinate, temperature, wind | 1 hour |
| Fuel | port, fuel type, price, currency, unit | 24 hours |
| FX | base/quote currencies, rate | 1 hour |
| Inventory | location, item, quantity, unit | 24 hours |
| Route/reference | route, endpoints, distance | 30 days |
| News/geopolitical | event, headline, region, severity, publication time | 24 hours |
| Congestion (synthetic/demo) | port, queue vessels, delay days, severity | scenario |
| Voyages (synthetic/demo) | vessel, route, departure, arrival, cargo volume | scenario |
| Contract alternatives (synthetic/demo) | strategy, rate, volume, validity, terms | scenario |

Connectors currently include `MockConnector`, `FileConnector` (JSON/JSONL), and
`SyntheticConnector`. They implement the same protocol and intentionally do not
contain provider-specific integrations.

## Data Docked

Data Docked is an optional external maritime/AIS provider. NAVISAIL may use it
for vessel location and future provider-backed vessel, port-call, route, and
enrichment capabilities through the backend adapter. Authentication is a
server-side API key. Observations are validated, normalized, quality-scored,
freshness-evaluated, and attributed as `LIVE` or `DELAYED`; cache fallback is
used only when configured. Provider rate limits, credits, outages, and schema
errors do not replace NAVISAIL's state, congestion, cost, optimization, or
recommendation engines.
