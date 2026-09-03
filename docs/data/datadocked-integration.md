# Data Docked integration

Data Docked is an optional external maritime provider. It is accessed only by
the backend adapter in `backend/app/data/connectors/datadocked/`, then mapped
into the existing `SourceRecord` contracts and source registry. It is not the
system of record and it does not make recommendations.

## Modes and configuration

Use `NAVISAIL_MODE=DEMO` for the deterministic offline scenario,
`NAVISAIL_MODE=SYNTHETIC` for generated local data, or `NAVISAIL_MODE=LIVE`
when external observations are explicitly enabled. Configure the provider with
the `DATADOCKED_*` variables in `.env.example`; keep the API key in the
deployment secret store only.

## Data flow

`DataDockedProvider` performs one centralized HTTP request path with bounded
timeouts, retries for transient failures, explicit 429/auth handling, an
in-memory TTL cache, and a credit guard. Responses are parsed by provider
schemas and mapped to canonical AIS source records. The registry applies
validation, freshness, quality, duplicate detection, quarantine, and lineage
before a record can reach a state snapshot.

The currently exposed NAVISAIL-owned surfaces are:

- `GET /api/v1/data-sources/datadocked/health`
- `POST /api/v1/data-sources/datadocked/vessels/location`

The adapter's endpoint paths are centralized in the client and must be checked
against the current Data Docked OpenAPI before enabling live deployment.

## Security and failure behavior

Credentials are never returned by health, events, errors, or frontend APIs.
The frontend never calls Data Docked. Disabled, unavailable, rate-limited,
malformed, or insufficient-credit responses fail explicitly and may use a
non-LIVE cached record when configured. No synthetic data is substituted unless
the explicit fallback setting is enabled.

## Testing and operations

Normal tests use `httpx.MockTransport` and do not require a provider key.
Optional live tests are disabled by default (`DATADOCKED_LIVE_TESTS=false`).
Monitor provider health, request failures, cache behavior, freshness, and
credit/rate-limit state before enabling background refresh.
