# Testing Strategy

NAVISAIL uses fast, deterministic checks at every change boundary.

## Test layers

- **Unit tests** cover pure domain functions and services without network or database access.
- **Integration tests** use disposable PostgreSQL/Redis services and verify repository boundaries.
- **API tests** use FastAPI's `TestClient` and assert status, response schemas, and correlation headers.
- **Frontend tests** use Vitest for pure utilities and component behavior; Next's typecheck and build are required gates.
- **End-to-end tests** cover only high-value decision journeys once those workflows exist.

Tests must not depend on wall-clock time, external APIs, or live credentials. Use fixed fixtures and seeds
for deterministic data. Business calculations belong in typed domain engines, not test doubles or UI code.

## Local commands

```bash
make test
make lint
make format
make typecheck
```

## Coverage

Backend coverage is collected with `pytest-cov` and must remain at least 75% during foundation work.
Coverage is a signal for
untested behavior, not a substitute for meaningful assertions. Frontend coverage will be added when the
first business utilities are introduced.
