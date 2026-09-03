# Test Matrix

| Area                | Runner              | Required checks                             | Test data                   |
| ------------------- | ------------------- | ------------------------------------------- | --------------------------- |
| Backend API         | pytest + httpx      | Health, version, status, response contract  | Deterministic fixtures      |
| Backend quality     | Ruff + mypy         | Lint, format, strict types                  | Source tree                 |
| Synthetic fixtures  | pytest              | Stable hashes, counts, and shock effects    | Fixed seed / DEMO scenario  |
| Persistence         | pytest integration  | Migrations, repositories, constraints       | Disposable Postgres/PostGIS |
| Forecasting         | pytest              | Chronological split, baseline, intervals    | Fixed time series           |
| Optimization        | pytest              | Hard constraints, infeasibility, relaxation | Fixed candidate set         |
| Frontend            | Vitest + TypeScript | Utilities, components, typecheck            | Static fixtures             |
| Frontend production | Next build          | Compilable production bundle                | No external secrets         |
| End-to-end          | Playwright          | Decision-session journeys                   | Seeded demo scenario        |

Every new feature should add the narrowest applicable test layer first, then integration coverage when
it crosses a persistence or external-system boundary.
