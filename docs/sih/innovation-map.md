# NAVISAIL Innovation Map

NAVISAIL's innovation is the composition of transparent maritime state,
probabilistic reasoning, optimization, and governed action into one decision
loop. The map below links the SIH product intent to the implementation that can
be demonstrated today.

| Innovation | What it does | Implementation evidence | Judge-visible proof |
| --- | --- | --- | --- |
| Maritime decision twin | Establishes one versioned state snapshot instead of disconnected dashboards. | `backend/app/maritime/state_vector.py`, `/maritime-state` | Command Center state context and Port Twin. |
| Predict | Separates source status, freshness, forecast intervals, calibration, and model metadata. | `backend/app/forecasting/`, `backend/app/data/` | Freight Intelligence uncertainty and provenance states. |
| Simulate | Tests congestion, outage, cyclone, fuel, vessel, delay, and inventory shocks against an immutable baseline. | `backend/app/risk/scenarios.py`, `monte_carlo.py`, `frontend/app/risk/` | Risk screen and deterministic congestion +5-day demo. |
| Optimize | Enforces vessel, port, berth, timing, cost, and supply constraints before ranking options. | `backend/app/optimization/`, compatibility, landed cost | Recommendation alternatives and infeasibility behavior. |
| Decide with explanation | Produces a recommendation with evidence, alternatives, assumptions, confidence, and a decision memo. | `backend/app/recommendations/`, `explainability/` | Recommendation screen and explainability API. |
| Human-governed action | Separates recommendation from approval and execution, with RBAC and audit history. | `backend/app/execution/`, `audit/`, `core/security.py` | Execution approval controls and readable Audit timeline. |
| Copilot transparency | Lets users ask decision questions while exposing approved tool activity and sources. | `backend/app/copilot/`, `dynamic_agents/` | Copilot retrieving/calculating/simulating/comparing states. |
| Digital twin continuity | Applies maritime events to voyage, vessel, port, and inventory state. | `backend/app/digital_twin/` | Spatial Port Twin plus event-driven state behavior. |
| Governed learning | Records model versions, chronological evaluation, feedback, drift, and promotion states. | `backend/app/mlops/`, `forecasting/evaluation/` | MLOps endpoints and audit provenance. |
| Truthful offline demonstration | Makes the SIH journey repeatable without pretending synthetic data is live. | `scripts/run_demo.py`, `backend/app/synthetic/` | Fixed seed/clock, `DEMO`/`SYNTHETIC` labels, stable output hash. |

## What is deliberately not claimed

The release demonstrates the intelligence and governance contracts with
deterministic inputs. It does not claim live AIS or market-provider coverage,
enterprise booking side effects, a cloud-hosted multi-worker queue, or a clean
automated browser test suite. Those are integration and operational workstreams,
not reasons to obscure the working decision-intelligence foundation.
