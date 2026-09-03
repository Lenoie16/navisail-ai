# Deployment and operations

NAVISAIL is deployed as a modular monolith with a separate worker process. The
production-like reference stack is [`docker-compose.prod.yml`](../../docker-compose.prod.yml):
backend API, Next.js frontend, PostgreSQL/PostGIS, Redis, a one-shot migration
job, and the worker heartbeat process.

## Environment

Start from [`.env.example`](../../.env.example). Production must provide
`POSTGRES_PASSWORD`, `AUTH_TOKEN`, and `REDIS_URL`. Compose defaults
`DATABASE_URL` to the internal `postgres` service; configure
`COMPOSE_DATABASE_URL` only for an intentional external database. Configure
`FRONTEND_URL`, `NEXT_PUBLIC_API_BASE_URL`, `APP_VERSION`, `APP_ENV`,
`LOG_LEVEL`, and `ENABLE_DOCS` for each environment. Set `ERROR_TRACKING_DSN`
only when an approved error-tracking service is configured.

Never commit `.env` files or put credentials in images. Use a deployment secret
store in shared environments.

## Startup order

1. PostgreSQL and Redis pass their container healthchecks.
2. The migration service runs `alembic upgrade head` and must complete.
3. The backend starts and must pass `/api/v1/health/ready`.
4. The worker starts after Redis and publishes its bounded heartbeat.
5. The frontend starts after backend readiness.

## Health and monitoring

- `/api/v1/health/live` checks process liveness only.
- `/api/v1/health/ready` checks PostgreSQL and Redis and returns `503` when a
  required dependency is unavailable.
- `/api/v1/data-health` reports source freshness and quarantine counts.
- `/api/v1/performance/metrics` reports bounded in-process request and domain
  timings; treat it as diagnostic data, not a durable time series.
- `navisail:worker:heartbeat` in Redis indicates that the worker loop is alive.

Collect stdout as structured JSON. Alert on readiness failures, HTTP 5xx/429
rates, slow requests, failed orchestration jobs, stale data, degraded model
metrics, and missing worker heartbeats. Error tracking must be configurable and
must not block request handling.

## Migrations and rollback

Build and deploy the image, run the migration job, then roll out API, worker,
and frontend containers. Migrations must remain backwards-compatible during a
rolling deployment. To roll back, redeploy the previous immutable image; do not
automatically downgrade schema revisions. Use a reviewed forward migration or
restore a backup for destructive changes.

## Backup and recovery

Back up PostgreSQL with encrypted, tested `pg_dump` or managed backups and
regularly test restores into an isolated database. Redis is a coordination/cache
dependency, not the system of record; its AOF volume is useful for recovery but
does not replace database backups. If Redis is unavailable, stop
queue-dependent work, restore Redis, and reconcile jobs using idempotency keys.

For an incident, inspect readiness and data-health, correlate structured logs
with `x-request-id` and correlation IDs, check migration and worker logs,
isolate the failing dependency, restore the last known-good image or backup,
and verify a read-only decision flow before reopening commercial actions.

## Local production-like run

```bash
cp .env.example .env
# Set POSTGRES_PASSWORD, AUTH_TOKEN, and REDIS_URL for Compose.
docker compose -f docker-compose.prod.yml --env-file .env up --build
```

This stack is suitable for repeatable staging/demo validation. Add TLS
termination, managed secrets, durable metrics/log storage, and network
policies before public exposure.
