# SIH Requirement Traceability

**Audit date:** 2026-09-03  
**Baseline:** NAVISAIL AI PRD v1.1 and the canonical SIH scenario  
**Verdict convention:** Complete means an implemented and tested contract exists;
Partial means a foundation or deterministic substitute exists but production
coverage is incomplete; Missing means no credible implementation evidence was
found; Out of scope means deliberately excluded from this release.

This is an evidence audit, not a claim that synthetic fixtures are live
maritime integrations. File paths are relative to the repository root.

| PRD / SIH requirement | Domain implementation | API / frontend surface | Test / demo evidence | Status and gap |
| --- | --- | --- | --- | --- |
| Product positioning: Predict → Simulate → Optimize → Decide | `backend/app/` modular domains; [README](../../README.md) | Command Center, Recommendation, Risk, Copilot screens | [canonical scenario](../demo/canonical-scenario.md) | **Complete** for the decision-support positioning; external SAIL-system integration remains future work. |
| Data architecture, quality, freshness, lineage | `backend/app/data/`; `backend/app/schemas/` | `/api/v1/data-health`, source status badges | `backend/tests/data/test_source_contracts.py`, `test_data_health.py` | **Complete** for typed envelopes, validation, quarantine, freshness, and lineage; provider ingestion is **Partial**. |
| Maritime state | `backend/app/maritime/state/`, `state_vector.py` | `/api/v1/maritime-state`; Command Center and Ports | `test_state_vector.py`, `test_maritime_state.py` | **Complete** for versioned session-scoped snapshots and comparison. |
| Freight forecasting and probabilistic outputs | `backend/app/forecasting/` | `/api/v1/forecasts`; Freight Intelligence | `backend/tests/forecasting/test_forecasting.py` | **Complete** for deterministic inference/evaluation/calibration contracts; live market feed and trained production artifact are **Partial**. |
| AIS and vessel intelligence | `backend/app/maritime/vessels/`; synthetic AIS generators | `/api/v1/maritime-state/vessels/*`; Ports | `test_vessel_intelligence.py`, `test_generators.py` | **Partial**: normalized/synthetic trajectories and candidate intelligence exist; live AIS provider, streaming ingestion, and coverage SLAs are not implemented. |
| Port and berth compatibility | `backend/app/maritime/compatibility/`, `ports/`; berth service | `/api/v1/compatibility`, Ports | `test_compatibility.py` | **Complete** for hard constraints and explicit failures over supplied inputs; live berth closures/depth/weather feeds are **Partial**. |
| Congestion prediction | `backend/app/congestion/` | `/api/v1/congestion`; Command Center / Ports | `backend/tests/congestion/test_congestion.py` | **Complete** for queue/prediction contracts; production historical feed and calibration monitoring are **Partial**. |
| Landed cost | `backend/app/landed_cost/` | `/api/v1/landed-cost`; Recommendation / Contracts | `test_landed_cost.py` | **Complete** for units, FX metadata, delay, disruption, inventory carrying cost, and risk multiplier calculations. |
| Optimization and infeasibility | `backend/app/optimization/` | `/api/v1/optimization`; Recommendation | `test_optimization.py`, `test_recommendation_engine.py` | **Complete** for hard constraints, deterministic ranking, and explicit infeasibility. |
| Charter Now / Wait | `backend/app/charter/` | `/api/v1/charter/timing`; Recommendation | `test_charter_timing.py` | **Complete** for Now, Wait, and Neutral/Indeterminate outcomes. |
| Contract strategy comparison | `backend/app/optimization/strategy.py`, `backend/app/models/contract.py` | `/api/v1/optimization/strategy`; Contracts | `test_strategy.py` | **Complete** for spot, COA, time-charter, and hybrid comparison over supplied alternatives. |
| Risk and Monte Carlo | `backend/app/risk/` | `/api/v1/risk/simulate`, `/compare`, `/regime`; Risk | `test_monte_carlo.py`, `test_market_regime.py` | **Complete** for fixed-seed distributions, percentiles, delay/inventory breach, and shocks. |
| Market regime and shocks | `backend/app/risk/regime.py`, `scenarios.py` | `/api/v1/risk/regime`; Risk | `test_market_regime.py`, demo shock | **Complete** for modeled state and deterministic shock comparison; live regime detection is **Partial**. |
| Digital twin | `backend/app/digital_twin/` | `/api/v1/digital-twin`; Ports spatial view | `test_digital_twin.py` | **Complete** for event application, state transitions, and inventory consumption; live telemetry connection is **Partial**. |
| Plant inventory and supply risk | `backend/app/supply/`, `backend/app/models/inventory.py` | `/api/v1/supply/project`; Command Center | `test_supply_risk.py`, `test_digital_twin.py` | **Complete** for projections and stockout effects with supplied data; ERP/inventory-system integration is **Partial**. |
| Recommendations and explainability | `backend/app/recommendations/`, `explainability/` | `/api/v1/recommendations/generate`, `/explainability/memo`; Recommendation | `test_recommendation_engine.py`, `test_explainability.py` | **Complete** for alternatives, evidence, reproducibility metadata, and decision memo structure. |
| Copilot and dynamic agents | `backend/app/copilot/`, `dynamic_agents/` | `/api/v1/copilot/*`; Copilot | `test_copilot.py`, `test_dynamic_agents.py` | **Complete** for approved tools, bounded budgets, failures, timeouts, and transparency; external LLM/model hosting is **Partial**. |
| Approval and execution | `backend/app/execution/`, `models/approval.py` | `/api/v1/execution/*`; Execution | `test_execution_workflow.py`, `test_security.py` | **Complete** for authorization-gated state transitions and demo-safe workflow; booking/TMS side effects are intentionally **Partial**. |
| Readable audit | `backend/app/audit/`, `routes/audit.py` | `/api/v1/execution/audit/*`; Audit | `test_execution_workflow.py` and API coverage | **Complete** for readable event/provenance records; immutable enterprise retention is **Partial**. |
| MLOps governance | `backend/app/mlops/`, `forecasting/evaluation/` | `/api/v1/mlops/*`; Audit metadata | `test_mlops_governance.py`, `test_forecasting.py` | **Complete** for registry, evaluation, drift/freshness, feedback, and promotion guards in-process; durable registry/artifact store is **Partial**. |
| Security, authentication, RBAC | `backend/app/core/security.py`, `api/middleware/auth.py` | Server-side route dependencies; hidden unavailable actions | `test_security.py` | **Complete** for release authorization boundaries and denied-action audit events; enterprise IdP/secret rotation is **Partial**. |
| Realtime events | `backend/app/events/`, `routes/events.py` | `/api/v1/events/stream`; frontend realtime hook/store | `test_orchestration.py`, frontend smoke coverage | **Partial**: typed bus, SSE, correlation IDs, deduplication, and reconnect logic exist; durable multi-instance broker delivery is not complete. |
| Deterministic SIH demo | `scripts/run_demo.py`, `backend/app/synthetic/` | Demo journey across all primary screens | `backend/tests/synthetic/test_demo_runner.py`, [demo script](../demo/demo-script.md) | **Complete** for fixed seed/clock, labels, stable hash, baseline preservation, congestion +5-day shock, and side-effect-free approval/execution. |
| Deployment and observability | Dockerfiles, Compose, health, logging, worker heartbeat | `/health/*`, `/performance/metrics` | Phase 42 validation and [deployment runbook](../architecture/deployment.md) | **Partial**: production-like local topology exists; durable queue, cloud provisioning, alert rules, and load/SLA evidence are not release-complete. |
| UX/accessibility | `frontend/components/ui`, `styles/globals.css` | Ten primary routes | frontend typecheck, lint, format, Vitest, Next build; browser inspection | **Partial**: responsive, semantic, focus, reduced-motion, and explicit states are implemented; automated browser E2E and formal contrast audit are unavailable. |

## Release gaps

1. Live AIS, freight, weather, berth, ERP, TMS, and identity-provider
   integrations are not represented as connected production feeds.
2. The worker publishes a Redis heartbeat, but the orchestration job state is
   still in-process rather than a durable distributed queue.
3. Browser E2E is listed in the test matrix but no Playwright configuration or
   tests exist; this is a validation-infrastructure gap, not evidence of
   failure.
4. Backend Ruff/mypy findings documented in
   [Phase 40 report](../testing/phase-40-report.md) prevent a clean quality-gate
   claim and are pre-existing.
5. Performance evidence is deterministic smoke validation, not a
   machine-independent latency SLA or production load test.

These gaps are explicitly retained rather than hidden or filled with fabricated
live values.
