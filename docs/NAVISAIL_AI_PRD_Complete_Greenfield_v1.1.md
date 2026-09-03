### NAVISAIL AI

### PRODUCT REQUIREMENTS DOCUMENT

AI-Powered Maritime Procurement & Chartering Digital Twin for SAIL Predict → Simulate → Optimize → Decide

### Document purpose

This PRD is the master product, product-behavior, architecture, data, AI/ML, optimization, UX, security, testing, deployment and release specification for NAVISAIL AI. It consolidates the supplied SIH problem material and NAVISAIL design baseline into a single implementation source of truth. This revision is explicitly greenfield: the repository is assumed to be created from scratch, with no legacy migration or retrofit requirements.

| **Field**            | **Value**                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| Document status      | Master PRD / Greenfeld Implementation Baseline                                                          |
| Problem statement    | SIH 2026 Problem Statement 26006 / SIH2026-095                                                          |
| Product              | NAVISAIL AI                                                                                             |
| Primary organization | Steel Authority of India Limited (SAIL)                                                                 |
| Domain               | Transportation & Logistics / Maritime Procurement                                                       |
| Document version     | 1.1                                                                                                     |
| Prepared             | September 2026                                                                                          |
| Build baseline       | Greenfeld repository; modular monolith frst; phased<br>implementation from Phase 0 to Release Candidate |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **Table of Contents**

###  1. Executive Summary

**_GREENFIELD BASELINE: NAVISAIL AI starts as a clean repository. No legacy audit, migration layer, compatibility shim or inherited architecture is required unless a concrete reusable artifact is intentionally introduced into the new repository._**

- 2. Product Vision and Positioning

|    | 3. Source and Scope Basis<br>                 |
| --- | --------------------------------------------- |
|    | 4. Problem Defnition                          |
|    | 5. Goals, Objectives and Success Criteria     |
|    | 6. Personas and Stakeholders                  |
|    | 7. Product Principles                         |
|    | 8. Product Scope and Release Strategy         |
|    | 9. End-to-End Decision Journey                |
|    | 10. Functional Architecture                   |
|    | 11. System Architecture                       |
|    | 12. Domain Model                              |
|    | 13. Data Architecture                         |
|    | 14. Maritime State Engine                     |
|    | 15. Freight Forecasting                       |
|    | 16. AIS and Vessel Intelligence               |
|    | 17. Port and Berth Intelligence               |
|    | 18. Port Congestion Prediction                |
|    | 19. Landed Cost Engine                        |
|    | 20. Optimization Engine                       |
|    | 21. Charter Now / Wait and Cost of Waiting    |
|    | 22. Contract Strategy Optimizer               |
|    | 23. Risk and Monte Carlo Engine               |
|    | 24. Market Regime and Shock Detection         |
|    | 25. Digital Twin                              |
|    | 26. Plant Inventory and Supply Risk           |
|    | 27. Recommendation and Explainability         |
|    | 28. AI Copilot and Dynamic Agent Layer        |
|    | 29. Execution, Approval and Audit             |
|    | 30. Frontend / UX Product Requirements        |
|    | 31. Screen-by-Screen Requirements             |
|    | 32. API Requirements                          |
|    | 33. Database Schema                           |
|    | 34. Event and Streaming Architecture          |
|    | 35. MLOps and Model Governance                |
|    | 36. Security and Governance                   |
|    | 37. Non-Functional Requirements               |
|    | 38. Testing and Validation Strategy           |
|    | 39. Synthetic Data and Demo Determinism       |
|    | 40. SIH Demo Experience                       |
|    | 41. Deployment and DevOps                     |
|    | 42. Observability and Operations              |
|    | 43. Accessibility and Usability               |
|    | 44. Risk Register                             |
|    | 45. Team Workstreams                          |
|    | 46. Phase-by-Phase Implementation Roadmap<br> |
|    | 47. Defnition of Done Framework               |
|    | 48. Acceptance Criteria                       |
|    | <br>49. KPIs and Measurement                  |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- 50. Future Roadmap

- 51. Appendix A — Final Repository Structure

- 52. Appendix B — Canonical Data Objects

- 53. Appendix C — API Catalog

- 54. Appendix D — Research and Source Basis

55. Appendix E — Functional Requirement Catalog

56. Appendix F — Non-Functional Requirement Catalog

57. Appendix G — Business Rules and Calculation Contracts

58. Appendix H — Release Acceptance Checklist

59. Appendix I — Glossary and Controlled Terminology

### **Reading rule**

This document is intentionally implementation-ready. Product requirements, architecture, technical requirements, acceptance criteria, and phase prompts are included so the PRD can be used directly as the project execution baseline.

# **1. Executive Summary**

NAVISAIL AI is a maritime procurement and chartering decision-support platform designed for SAIL. Its core purpose is to transform freight-market intelligence into an explainable procurement decision. The system is explicitly not positioned as a standalone freight-rate prediction dashboard.

The platform accepts a cargo requirement and determines the economically and operationally preferred combination of booking timing, vessel strategy, port/berth, route, contract structure and risk posture. It evaluates expected landed logistics cost, downside risk, schedule reliability and plant supply impact before producing a recommendation.

The product follows the operating loop: Predict → Simulate → Optimize → Decide. This reflects the supplied SIH concept, which describes freight forecasting, digital twin simulation, smart optimization, risk/scenario analysis, explainable decisions, alerts and execution/tracking as core platform capabilities. [Source: supplied NAVISAIL design notes]

The SIH source identifies the problem as one involving freight forecasting, vessel chartering and bulk-cargo procurement from overseas sources to the East Coast of India. The supplied proposal also identifies multiple vessel classes, East Coast ports and the need for better chartering and procurement decisions. [Source: supplied NAVISAIL design notes]

### **Product promise**

Given X tonnes of cargo from origin O to plant P by date D, NAVISAIL determines WHEN to book, WHICH vessel strategy to use, WHERE to discharge, WHICH contract structure to use, WHAT the risk-adjusted landed cost is, and WHY the recommendation is preferred.

# **2. Product Vision and Positioning**

## **2.1 Vision**

Build a trusted maritime intelligence layer that helps SAIL move from reactive spot-chartering decisions toward predictive, risk-aware and auditable multi-voyage procurement.

## **2.2 Positioning**

NAVISAIL is an AI intelligence and optimization layer that can sit above SAIL procurement systems and integrate with India's maritime digital ecosystem; it is not positioned as a replacement for every existing operational system. The prior concept explicitly describes this integration-layer position. [Source: supplied NAVISAIL design notes]

## **2.3 Core value proposition**

- Forecast route- and vessel-class-specific freight conditions across 7/15/30/90-day horizons.

- Fuse AIS, port, market, commodity, weather, fuel, FX, news and operational signals into a common maritime state.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- Identify physically feasible vessel and berth combinations.

- Optimize total landed logistics cost instead of ocean freight alone.

- Quantify uncertainty through probabilistic forecasts and scenario simulation.

- Compare spot, COA, time-charter and hybrid procurement strategies.

- Give an explainable recommendation with traceable data and model lineage.

- Allow human approval before commercial execution.

- Close the loop by comparing forecast/plan with actual voyage outcomes.

# **3. Source and Scope Basis**

This PRD is grounded primarily in the uploaded SIH proposal PDF and the accompanying prior NAVISAIL design notes. The supplied SIH PDF identifies the project as SIH2026-095, problem statement 26006, with the title “Development of an Intelligent Freight Forecasting Model for Optimized Vessel Chartering and Bulk Cargo Procurement from overseas to East Coast of India.” [Source: supplied NAVISAIL design notes]

## **3.1 Supplied source elements incorporated**

- SIH framing and maritime procurement/chartering context.

- Forecasting across freight and vessel classes.

- Digital twin simulation.

- Optimization and landed-cost focus.

- Risk and scenario analysis.

- Real-time alerts and explainable decisions.

- Execution/tracking concept.

- Premium dashboard direction with Command Center, Freight Intelligence, Shipment Planning, AI Recommendation, Port Digital Twin, Contract Simulator and Risk/Scenario Center.

- Existing Dynamic Agent V2 architecture and its shared-context/EventBus/SSE/recovery ideas, to be reused only where appropriate.

## **3.2 Research basis in supplied SIH PDF**

The supplied submission cites research covering freight-rate forecasting, dry-bulk freight forecasting, voyage charter-party optimization, port congestion estimation/prediction, ship waiting-time prediction and digital-twin architectures. [Source: supplied NAVISAIL design notes]

# **4. Problem Definition**

## **4.1 Business problem**

SAIL chartering decisions depend on the interaction of market price, vessel availability, port constraints, congestion, weather, cargo schedule, contract structure and plant requirements. A freight forecast alone is therefore insufficient.

## **4.2 Decision problem**

For every shipment or procurement programme, NAVISAIL must answer:

- Should we book now, wait, book within a defined window, or hedge?

- Which vessel class or combination is best?

- Which port and berth can physically and operationally accept the candidate vessel?

- Which route and schedule minimize total landed cost and risk?

- Which contracting strategy is economically robust?

- What is the probability of meeting laycan/plant need?

- What events could invalidate the decision?

- How does the decision change under disruption?

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

## **4.3 Problem boundaries**

NAVISAIL is a decision-support system. It should not autonomously execute a binding charterparty without human authorization. AI generates analyses and recommendations; designated users approve or modify them; execution actions are audited.

# **5. Goals, Objectives and Success Criteria**

## **5.1 Product goals**

- Reduce uncertainty around freight procurement decisions.

- Reduce total landed logistics cost.

- Improve vessel and port utilization.

- Reduce manual analysis time.

- Increase schedule reliability.

- Make decisions explainable and auditable.

- Provide what-if capability for operational disruptions.

- Create a reusable platform architecture rather than a one-off demo.

## **5.2 Success criteria**

| **Area**       | **Target / Evidence**                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------ |
| Forecasting    | Probabilistic 7/15/30/90-day forecasts with walk-forward evaluation<br>and documented confdence. |
| Optimization   | Feasible vessel/port/timing/contract recommendations with<br>alternative solutions.              |
| Cost           | Explicit landed-cost decomposition and risk-adjusted cost.                                       |
| Risk           | Scenario distributions, P90/P95 and CVaR outputs.                                                |
| Digital twin   | Parameter changes propagate to ETA, inventory, cost and<br>recommendation.                       |
| Explainability | Every recommendation exposes factors, assumptions and<br>counterfactuals.                        |
| Audit          | Data snapshot, model version, optimization run and human action are<br>stored.                   |
| UX             | Seven primary screens feel like one connected decision workspace.                                |
| Reliability    | Core demo works deterministically without dependency on unstable<br>external feeds.              |

# **6. Personas and Stakeholders**

| **Persona**              | **Primary needs**                                  | **Key actions**                                  |
| ------------------------ | -------------------------------------------------- | ------------------------------------------------ |
| Chartering Manager       | timing, vessel, charter options, market<br>outlook | plan shipment, optimize, compare, approve        |
| Procurement / Commercial | contract strategy, expected cost, downside<br>risk | compare spot/COA/hybrid, review decision<br>memo |
| Operations Manager       | port/berth feasibility, congestion, ETA            | inspect twin, validate port and vessel           |
| Plant / Supply Planner   | inventory, inbound timing, stockout risk           | review plant exposure and shipment<br>scenarios  |
| Leadership               | cost, savings, risk, portfolio view                | Command Center, executive summaries              |
| IT / Data / ML           | data quality, model health, APIs, lineage          | manage sources, models, monitoring               |
| Auditor / Governance     | decision traceability                              | audit recommendation and approval history        |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **7. Product Principles**

- Decision first: every intelligence feature must support a business decision.

- Numerical truth outside the LLM: cost, forecast, optimization and risk figures originate from typed services/models.

- One shared maritime state: downstream engines must operate from a common Maritime State Vector.

- Physical feasibility before economics: infeasible vessels/berths are filtered or penalized before commercial ranking.

- Risk-adjusted economics: optimize expected landed cost plus explicit downside risk.

- Human-in-the-loop: commercial execution requires human approval.

- Auditable by construction: decisions store data, model, constraints and rationale.

- Honest data status: LIVE, DELAYED, ESTIMATED and SYNTHETIC are always distinguishable.

- Progressive complexity: modular monolith before distributed microservices.

- One decision session across UI: all primary screens share the same state and recommendation context.

# **8. Product Scope and Release Strategy**

## **8.1 MVP**

- Freight forecasting

- Shipment planner

- Vessel recommendation

- Port/berth compatibility

- Charter Now/Wait

- Landed-cost comparison

- Command Center and core recommendation UI

## **8.2 SIH final**

- AIS intelligence

- Port congestion prediction

- Probabilistic forecasting

- Monte Carlo scenarios

- Multi-voyage contract optimization

- News/geopolitical risk

- Digital twin

- Explainable AI

- Audit trail

- AI copilot

This release strategy is consistent with the earlier NAVISAIL plan, which separates the internal-round MVP from the richer final feature set. [Source: supplied NAVISAIL design notes]

# **9. End-to-End Decision Journey**

```
User creates shipment
```

```
        ↓
Validate cargo / plant / date
```

```
        ↓
Load Maritime State Snapshot
```

```
        ↓
Forecast freight
```

```
        ↓
Calculate vessel supply
```

```
        ↓
Predict port congestion
```

```
        ↓
```

```
Generate vessel candidates
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
        ↓
Check port + berth compatibility
        ↓
Calculate landed cost
        ↓
Evaluate booking dates
        ↓
Evaluate contract strategies
        ↓
Run risk scenarios
        ↓
Optimize
        ↓
Rank alternatives
        ↓
Generate Recommendation
        ↓
Explain WHY / WHAT COULD GO WRONG
        ↓
Human Approval
        ↓
Execution / Tracking
        ↓
Actuals
        ↓
Model / Decision Feedback
```

# **10. Functional Architecture**

```
Experience Layer
 ├── Command Center
 ├── Freight Intelligence
 ├── Plan Shipment
 ├── Recommendation
 ├── Port Digital Twin
 ├── Contract Simulator
 ├── Risk & Scenario Center
 └── Copilot / Execution / Audit
```

```
Decision Intelligence
 ├── Maritime State Engine
 ├── Freight Forecasting
 ├── AIS / Vessel Intelligence
 ├── Port / Berth Intelligence
 ├── Congestion Prediction
 ├── Landed Cost
 ├── Optimization
 ├── Contract Strategy
 ├── Risk / Monte Carlo
 ├── Digital Twin
 ├── Inventory / Plant Risk
 └── Recommendation / XAI
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
Foundation
 ├── Data Ingestion
 ├── Data Quality / Freshness
 ├── PostgreSQL + PostGIS
 ├── Redis / Workers
 ├── Events / SSE
 ├── Audit / Lineage
 └── MLOps
```

# **11. System Architecture**

The system should be implemented initially as a modular monolith with clear domain boundaries. The submitted architecture diagram lists ingestion, data platform, AI/analytics, services, presentation and outcomes, and the proposed technology stack includes React/TypeScript, Python/FastAPI, XGBoost/scikit-learn/PyTorch, OR-Tools, PostGIS, PostgreSQL, Docker and AWS. [Source: supplied NAVISAIL design notes]

### **Architecture decision**

Do not introduce a dozen microservices at the prototype stage. Keep a single FastAPI application with domain modules, background workers, PostgreSQL/PostGIS and Redis. Services can later be extracted without changing contracts.

# **12. Domain Model**

| **Entity**       | **Purpose**                        | **Core attributes**                                                                      |
| ---------------- | ---------------------------------- | ---------------------------------------------------------------------------------------- |
| Shipment         | cargo movement requirement         | quantity, commodity, origin, destination<br>plant, required date, laycan, risk tolerance |
| Vessel           | physical ship                      | IMO, class, DWT, LOA, beam, draft, speed,<br>fuel, location                              |
| Port             | discharge/load location            | location, channel, congestion, handling<br>capability                                    |
| Berth            | specifc port handling point        | LOA, beam, draft, DWT, cargo, operational<br>restrictions                                |
| Route            | origin-destination movement        | distance, duration, route risk                                                           |
| Forecast         | future market estimate             | horizon, P10/P50/P90, model version                                                      |
| OptimizationRun  | candidate optimization computation | decision variables, objective, constraints,<br>result                                    |
| ScenarioRun      | what-if computation                | parameters, seed, results, metrics                                                       |
| ContractStrategy | procurement structure              | spot/COA/time charter/hybrid, share                                                      |
| Recommendation   | fnal ranked decision               | action, vessel, port, timing, contract, cost,<br>risk, confdence                         |
| Voyage           | actual movement                    | planned/actual dates, status, costs, events                                              |
| Inventory        | plant supply state                 | stock, consumption, safety stock, inbound                                                |
| AuditEvent       | traceability                       | actor, action, timestamp, snapshot, decision                                             |

# **13. Data Architecture**

## **13.1 Data domains**

- Freight market: BDI/BCI/BPI/BSI, route rates and time-charter rates.

- Commodity and macro: coal, iron ore, oil, fuel, FX, demand indicators.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- AIS/vessel: position, speed, heading, draft, destination, ETA.

- Port: berth dimensions, congestion, queues, handling, tide, turnaround.

- External risk: weather, cyclones, geopolitics, maritime news, closures.

- SAIL/internal: contracts, bids, laycan, nominations, demurrage, plant demand, inventories and schedules, simulated if unavailable for SIH.

These categories follow the data architecture described in the prior NAVISAIL material. [Source: supplied NAVISAIL design notes]

## **13.2 Source contract**

```
DataSource
 ├── source_name
 ├── source_type
 ├── last_success
 ├── status: LIVE | DELAYED | ESTIMATED | SYNTHETIC
 ├── quality_score
 ├── freshness_seconds
 └── schema_version
```

# **14. Maritime State Engine**

The Maritime State Engine is the central fusion layer. It converts heterogeneous market, vessel, port, weather, commodity, fuel, FX and geopolitical signals into a versioned Maritime State Vector that every downstream intelligence engine can consume.

## **14.1 State vector**

```
MaritimeStateVector
  timestamp
  market_state
  freight_state
  vessel_supply_state
  port_state
  route_state
  weather_state
  commodity_state
  fuel_state
  fx_state
  geopolitical_state
  market_regime
  data_quality_state
  snapshot_id
```

## **14.2 Requirements**

- Build deterministic aggregators for vessel supply, port queues, route capacity and market indicators.

- Persist state snapshots for reproducibility.

- Attach data freshness and quality to every state component.

- Emit MARITIME_STATE_UPDATED events.

- Expose GET /api/v1/maritime-state and historical snapshot retrieval.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **15. Freight Forecasting**

## **15.1 Forecast targets**

Forecast vessel-class and route-level freight across 7, 15, 30 and 90 days. Supported classes are Capesize, Panamax, Supramax and Handysize. Supported origin families should include Australia, Mozambique, USA, Indonesia and Russia, consistent with the prior design direction.

## **15.2 Feature families**

- Lagged and rolling freight features

- BDI/BCI/BPI/BSI and route rates

- Bunker/fuel prices

- Commodity prices

- FX

- Vessel supply and AIS density

- Port congestion

- Weather

- News/geopolitical features where available

## **15.3 Model stack**

```
Baseline: Naive / Moving Average / ARIMA or SARIMA
```

```
Primary: XGBoost or LightGBM
```

```
Sequence model: LSTM / TFT / Transformer only if validation justifies it
```

```
Final: weighted ensemble
```

```
Uncertainty: quantile / interval prediction
```

## **15.4 Evaluation**

- Walk-forward / time-aware validation

- MAE

- RMSE

- sMAPE/MAPE where appropriate

- Directional accuracy

- Interval coverage

- Pinball loss for quantile forecasts

- Business metric: decision savings vs baseline

# **16. AIS and Vessel Intelligence**

AIS processing must convert vessel positions into operational intelligence rather than simply plotting dots on a map.

```
AIS record
```

- `↓`

```
Track reconstruction
```

```
 ↓
```

```
Sailing / Anchorage / Berth classification
```

```
 ↓
Port association / geofence
```

```
 ↓
```

```
Voyage segmentation
```

```
 ↓
```

```
Fleet supply + queue + turnaround metrics
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

## **16.1 Vessel intelligence outputs**

- Vessel availability by class

- Ballast vs laden supply

- Regional vessel density

- Predicted availability during laycan

- Vessel ETA

- Speed and fuel estimates

- Compatibility score

# **17. Port and Berth Intelligence**

Port compatibility must be berth-aware. The prior proposal highlights materially different physical restrictions among East Coast ports and specifically emphasizes berth-specific LOA, beam and draft constraints. [Source: supplied NAVISAIL design notes]

## **17.1 Compatibility rules**

```
Physical
```

```
  vessel.LOA <= berth.max_LOA
  vessel.beam <= berth.max_beam
  vessel.draft <= effective_draft
  vessel.DWT <= berth.max_DWT
  cargo in supported_commodities
```

```
Operational
  tide restriction satisfied
  weather restriction satisfied
  daylight restriction satisfied
```

```
Schedule
```

```
  vessel availability overlaps laycan
  ETA <= required date
```

## **17.2 Outputs**

- Physical compatibility

- Operational compatibility

- Schedule compatibility

- Overall compatibility score

- Constraint/reason codes

# **18. Port Congestion Prediction**

Build a congestion engine based on berth occupancy, anchorage queue, arrival rates, handling capacity, historical waiting, AIS-derived port states and weather where relevant.

| **Output**         | **Description**                    |
| ------------------ | ---------------------------------- |
| Current congestion | 0–100 operational state score      |
| 7-day congestion   | predicted congestion distribution  |
| Expected wait      | mean/median wait days              |
| P90/P95 wait       | downside waiting exposure          |
| Demurrage exposure | estimated cost from waiting        |
| Confdence          | quality of the congestion estimate |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **19. Landed Cost Engine**

The platform must optimize total landed logistics cost rather than ocean freight alone. This is a central requirement from the prior design. [Source: supplied NAVISAIL design notes]

```
Total Landed Cost =
```

```
  Ocean Freight
+ Bunker
```

```
+ Port Charges
```

```
+ Waiting
```

```
+ Demurrage
```

```
+ Handling
```

```
+ Inland Logistics
```

- `+ Risk Cost`

Risk-adjusted cost should support: RiskAdjustedCost = ExpectedCost + lambda × CVaR.

## **19.1 Cost traceability**

Every cost output must carry assumptions and units. Users should be able to drill from total cost to component cost to underlying source/assumption.

# **20. Optimization Engine**

Use Google OR-Tools or equivalent constraint optimization for vessel, port, timing, route and contract decisions. Do not encode vessel selection as simple if/else business rules.

## **20.1 Decision variables**

- Vessel or vessel combination

- Number of vessels

- Port

- Berth

- Route

- Booking date

- Contract strategy

## **20.2 Hard constraints**

- Capacity

- Availability

- Draft

- LOA

- Beam

- DWT

- Cargo compatibility

- Laycan

- ETA

- Berth capability

- Plant requirement

## **20.3 Soft constraints / penalties**

- Congestion

- Weather risk

- Inventory exposure

- Demurrage risk

- Fuel exposure

- Route risk

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- CO2/sustainability preference

## **20.4 Outputs**

- Best feasible solution

- Second/third-best alternatives

- Objective decomposition

- Constraint satisfaction

- Trade-off explanation

# **21. Charter Now / Wait and Cost of Waiting**

### **Signature capability**

Charter Now / Wait is the hero decision feature. It converts freight forecasting into an economically explicit booking-window recommendation.

## **21.1 Booking-date evaluation**

Evaluate current day through a configurable future window (for example 30 days). For each candidate booking date, recompute forecast cost, vessel supply, port risk, inventory risk and expected risk-adjusted landed cost.

## **21.2 Cost of Waiting**

```
COW(t) =
  ExpectedFutureCost(t) - CurrentCost
```

```
+ InventoryRisk(t)
```

```
+ CongestionRisk(t)
```

- `+ SupplyRisk(t)`

## **21.3 Decision outputs**

- BOOK_NOW

- WAIT

- BOOK_WITHIN_WINDOW

- HEDGE

- Optimal booking start/end

- Probability of saving

- Downside if waiting is wrong

# **22. Contract Strategy Optimizer**

For repeated procurement, compare spot, COA, time charter and hybrid strategies over the required horizon.

| **Strategy**       | **Required analysis**                                    |
| ------------------ | -------------------------------------------------------- |
| 100% Spot          | expected cost, P90/P95, schedule risk, fexibility        |
| COA / multi-voyage | contracted capacity, expected cost, downside, fexibility |
| Time Charter       | daily hire, bunker, utilization, duration risk           |
| Hybrid             | contract/spot mix, downside protection, fexibility       |
| Custom mix         | user-specifed percentages, constraints and sensitivity   |

The prior design presents multi-voyage contracting as a key final-round differentiator and explicitly compares hybrid strategies. [Source: supplied NAVISAIL design notes]

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **23. Risk and Monte Carlo Engine**

The scenario engine should model uncertainty over freight, fuel, congestion, weather, vessel availability, FX, commodity demand, route disruption, port turnaround and plant supply risk.

## **23.1 Scenario architecture**

```
Base State
  ↓
Sample risk variables
  ↓
Apply correlations / constraints
  ↓
Simulate voyage + costs + ETA + inventory
  ↓
Store scenario outcome
  ↓
Aggregate distribution
  ↓
P50 / P90 / P95 / VaR / CVaR
```

## **23.2 Operational requirements**

- Run asynchronously for large batches.

- Support deterministic seeds for demo reproducibility.

- Persist scenario parameters and model versions.

- Stream progress using SSE.

- Allow side-by-side strategy comparison.

# **24. Market Regime and Shock Detection**

| **Regime**      | **Interpretation**               | **Policy impact**                                    |
| --------------- | -------------------------------- | ---------------------------------------------------- |
| NORMAL          | stable market                    | normal confdence/risk weight                         |
| TIGHTENING      | supply tightening / rates rising | earlier booking sensitivity                          |
| HIGH VOLATILITY | unstable rates                   | wider intervals, conservative risk weighting         |
| DISRUPTION      | operational disruption           | scenario-frst planning, stronger downside<br>penalty |
| CRISIS          | severe systemic disruption       | conservative mode / human review<br>escalation       |

The regime engine should lower confidence or change recommendation policy when conditions are outside the model's stable operating region.

# **25. Digital Twin**

The NAVISAIL digital twin models the cargo-to-plant chain: origin → loading port → vessel → ocean route → Indian port → berth → discharge → inland movement → plant → inventory.

## **25.1 Twin state**

- Vessel location

- Voyage phase

- ETA/ETD

- Port state

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- Berth

- Queue

- Weather

- Fuel

- Freight

- Inventory

- Cost

- Risk

## **25.2 State propagation example**

```
Paradip outage +5 days
```

```
 ↓
Port ETA changes
 ↓
Vessel schedule changes
 ↓
Plant ETA changes
 ↓
Inventory risk changes
 ↓
Demurrage / cost changes
 ↓
Risk changes
 ↓
Contract strategy changes
 ↓
```

```
Recommendation changes
```

This is the flagship “what-if” interaction: one operational change must flow through the entire decision graph rather than simply changing one UI label. The prior concept explicitly uses a five-day Paradip outage as the memorable re-optimization scenario. [Source: supplied NAVISAIL design notes]

# **26. Plant Inventory and Supply Risk**

Connect maritime decisions to plant-level supply conditions. Inventory should affect the objective function rather than be a decorative KPI.

- Current stock

- Daily consumption

- Safety stock

- Target stock

- Inbound shipments

- Days of cover

- Projected stockout date

- Stockout probability

### **Business rule**

When inventory is comfortable, waiting can be economically preferred. When inventory is critical, schedule reliability and stockout avoidance must receive higher weight in optimization.

# **27. Recommendation and Explainability**

## **27.1 Unified recommendation object**

```
Recommendation
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
 ├── action
 ├── booking_window
 ├── vessel_strategy
 ├── port_strategy
 ├── route_strategy
 ├── contract_strategy
 ├── expected_cost
 ├── p95_cost
 ├── cvar
 ├── expected_saving
 ├── laycan_probability
 ├── stockout_probability
 ├── forecast_confidence
 ├── decision_confidence
 ├── factors[]
 ├── alternatives[]
 ├── constraints[]
 ├── state_snapshot_id
 └── model_versions[]
```

## **27.2 Explanation requirements**

- Why this booking date?

- Why this vessel?

- Why this port/berth?

- Why this contract?

- Why is this cheaper/riskier?

- What alternatives were rejected?

- What could invalidate the recommendation?

- What data or assumptions are weak?

## **27.3 Confidence**

Forecast Confidence and Decision Confidence are distinct. Forecast Confidence relates to the predictive model; Decision Confidence reflects how robustly the selected option dominates alternatives given constraints and risk.

# **28. AI Copilot and Dynamic Agent Layer**

The LLM should sit above the deterministic domain engines. It may retrieve, explain, compare, classify, summarize and orchestrate tool calls. It must not become the source of financial or physical truth.

## **28.1 Tools**

- get_maritime_state()

- get_forecast()

- get_vessel_candidates()

- check_compatibility()

- get_port_state()

- compare_ports()

- calculate_landed_cost()

- optimize_charter()

- optimize_contract()

- run_scenario()

- get_inventory()

- get_recommendation()

- generate_decision_note()

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

## **28.2 Dynamic Agent V2 reuse**

The existing Dynamic Agent V2 patterns can be reused for orchestration: shared context, EventBus, SSE, lifecycle management, recovery/error wrappers and confidence/timeline concepts. The agents should remain isolated from core deterministic procurement calculations.

```
Agent / Copilot
```

```
      ↓
```

```
Intent classification
```

```
      ↓
Tool plan
      ↓
NAVISAIL domain tools
      ↓
Structured result
```

```
      ↓
Explanation / response
```

# **29. Execution, Approval and Audit**

```
DRAFT
```

```
 → RECOMMENDED
```

```
 → UNDER_REVIEW
```

```
 → APPROVED
```

```
 → BOOKED
```

```
 → LOADING
```

```
 → SAILING
```

```
 → ANCHORAGE
```

```
 → BERTHING
```

```
 → DISCHARGING
```

```
 → INLAND
```

```
 → DELIVERED
```

```
 → CLOSED
```

## **29.1 Approval**

The system must support approve, reject and modify actions with user identity, timestamp and reason. AI is advisory; humans retain commercial authority.

## **29.2 Audit contents**

- Input shipment

- Data snapshot

- Source freshness

- Forecast version

- Model version

- Candidate vessels/ports

- Constraints

- Optimization result

- Recommendation

- Human decision

- Actual outcome

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **30. Frontend / UX Product Requirements**

The frontend should preserve the supplied premium command-center visual direction: maritime dark theme, glassmorphism, 3D depth, high-information density, and restrained motion. The visual layer must serve the decision workflow rather than become decoration.

## **30.1 Design language**

- Deep ocean / midnight background

- Layered glass surfaces

- Soft edge highlights

- Technical thin borders

- Controlled glow

- 3D vessel / port objects

- Animated route arcs

- Premium data visualizations

- Strong hierarchy for recommendations

## **30.2 Glassmorphism rules**

- Use glass primarily for floating controls, decision panels, AI surfaces and map overlays.

- Use denser surfaces for tables, forms and high-density data.

- Maintain text contrast.

- Support hover, pressed, loading, disabled and keyboard states.

- Avoid excessive blur, transparency and constant motion.

## **30.3 3D rules**

Three-dimensional content should communicate physical maritime relationships: vessel location, route, port/berth geometry and digital-twin state. Lazy-load 3D scenes and support reduced-motion/accessibility settings.

# **31. Screen-by-Screen Requirements**

## **31.1 Command Center**

- KPI cards: cargo under planning, projected spend, AI savings, high-risk shipments, optimal charter windows.

- Interactive maritime map with vessels, routes, ports and alerts.

- Priority actions.

- Data health/freshness.

- Active recommendations.

## **31.2 Freight Intelligence**

- Vessel-class tabs: Capesize/Panamax/Supramax/Handysize.

- Route selector.

- Historical + forecast chart.

- P10/P50/P90 bands.

- 7/15/30/90-day controls.

- Forecast Confidence, data freshness and market regime.

- Cost-of-Waiting curve.

- Origin/trade-flow intelligence.

## **31.3 Plan Shipment**

- Commodity, quantity, origin, port, destination plant, required date, laycan, risk tolerance, contract preference.

- Optimize Charter CTA.

- Progress stream through pipeline stages.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

## **31.4 AI Recommendation**

- Dominant action such as WAIT X DAYS.

- Forecast Confidence + Decision Confidence.

- Vessel/route/port/contract.

- Expected landed cost, P95/CVaR and savings.

- WHY panel.

- What could make it wrong.

- Alternatives.

- Generate Decision Note.

- Request Approval.

## **31.5 Port Digital Twin**

- Map/3D scene.

- Port and berth cards.

- Vessel inspector.

- Compatibility.

- Congestion and waiting.

- Port comparison matrix.

## **31.6 Contract Simulator**

- Spot/COA/Time Charter/Hybrid.

- Contract-vs-spot allocation slider.

- Expected/P90/P95/CVaR.

- Risk/flexibility/capacity.

- Scenario comparison.

## **31.7 Risk & Scenario Center**

- Freight/fuel/congestion/weather/FX/geopolitical/vessel controls.

- Simulate 10,000 scenarios.

- Distribution chart.

- P50/P90/P95/CVaR.

- Laycan and stockout probabilities.

## **31.8 Copilot / Secondary surfaces**

- Natural-language query.

- Tool execution timeline.

- Grounded answers.

- Execution tracking.

- Audit trail.

- Model/data health.

# **32. API Requirements**

| **Group**                              | **Endpoints**                                                                    |
| -------------------------------------- | -------------------------------------------------------------------------------- |
| Health                                 | GET /api/v1/health; GET /api/v1/health/database; GET /api/v1/health/redis        |
| Shipments                              | POST /api/v1/shipments; GET /api/v1/shipments/{id}                               |
| Maritime State                         | GET /api/v1/maritime-state; GET /api/v1/maritime-state/{timestamp}               |
| Vessels                                | GET /api/v1/vessels; GET /api/v1/vessels/{id}; GET<br>/api/v1/vessels/candidates |
| Ports                                  | GET /api/v1/ports; GET /api/v1/ports/{id}; GET /api/v1/ports/{id}/berths         |
| Forecast                               | GET /api/v1/forecast; POST /api/v1/forecast/run                                  |
| Congestion                             | GET /api/v1/congestion/{port_id}; POST /api/v1/congestion/predict                |
| NAVISAIL AI — Product Requirements Doc | ument v1.1 — Greenfeld Implementation Baseline                                   |

| **Group**       | **Endpoints**                                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Compatibility   | POST /api/v1/compatibility/check                                                                                                        |
| Cost            | POST /api/v1/cost/estimate; GET /api/v1/cost/{optimization_id}                                                                          |
| Optimization    | POST /api/v1/optimization/vessel; POST /api/v1/optimization/port;<br>POST /api/v1/optimization/route; POST /api/v1/optimization/charter |
| Contracts       | POST /api/v1/contracts/simulate; POST /api/v1/contracts/optimize; GET<br>/api/v1/contracts/{run_id}                                     |
| Scenarios       | POST /api/v1/scenarios/run; GET /api/v1/scenarios/{id}; GET<br>/api/v1/scenarios/{id}/progress                                          |
| Digital Twin    | POST /api/v1/digital-twin/simulate; GET /api/v1/digital-twin/{shipment_id}                                                              |
| Recommendations | GET /api/v1/recommendations/{id}                                                                                                        |
| Copilot         | POST /api/v1/copilot/query; POST /api/v1/copilot/decision-note                                                                          |
| Execution       | GET /api/v1/execution/{shipment_id}                                                                                                     |
| Approvals       | POST /api/v1/approvals/{id}/approve; POST /api/v1/approvals/{id}/reject                                                                 |
| Audit           | GET /api/v1/audit/{recommendation_id}                                                                                                   |

# **33. Database Schema**

| **Table**           | **Important felds / notes**                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| shipments           | shipment_id, commodity, quantity_mt, origin_port, destination_plant,<br>required_by, laycan, risk_tolerance, status |
| vessels             | imo, name, class, dwt, loa_m, beam_m, draft_m, speed_knots,<br>fuel_mt_day, coordinates, ETA                        |
| vessel_positions    | vessel_id, timestamp, location, speed, heading, draft, destination                                                  |
| vessel_availability | vessel_id, availability_window, source, confdence                                                                   |
| ports               | port_id, name, coordinates, channel_depth, congestion_score,<br>waiting_days, handling_rate                         |
| berths              | berth_id, port_id, max_loa, max_beam, max_draft, max_dwt,<br>supported_commodities, restrictions                    |
| port_congestion     | port_id, timestamp, occupancy, queue, waiting, forecast, confdence                                                  |
| routes              | route_id, origin, destination, distance, duration, risk                                                             |
| freight_rates       | route, vessel_class, timestamp, rate, source                                                                        |
| forecasts           | forecast_id, route, vessel_class, timestamp, horizon, p10, p50, p90,<br>model_version                               |
| optimization_runs   | run_id, shipment_id, objective, constraints, result, version                                                        |
| scenario_runs       | run_id, seed, parameters, status, created_at                                                                        |
| scenario_results    | scenario_run_id, strategy, cost, ETA, stockout, laycan, risk                                                        |
| contracts           | contract_id, type, share, duration, rate, constraints                                                               |
| recommendations     | recommendation_id, shipment_id, action, timing, vessel, port,<br>contract, cost, risk, confdence                    |
| voyages             | voyage_id, shipment_id, planned/actual dates, status, cost, events                                                  |
| inventory           | plant_id, stock, consumption, safety_stock, inbound, projection                                                     |
| audit_events        | actor, timestamp, action, snapshot, model_version,<br>recommendation_id                                             |
| model_versions      | model_id, version, features, metrics, artifact_path                                                                 |
| data_sources        | source, status, freshness, quality, schema_version                                                                  |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **34. Event and Streaming Architecture**

Reuse the earlier EventBus approach where technically appropriate. Use SSE for long-running optimization, Monte Carlo and copilot streaming; WebSockets may be introduced later if required for bidirectional live feeds.

- DATA_UPDATED

- MARITIME_STATE_UPDATED

- FORECAST_STARTED

- FORECAST_COMPLETED

- CONGESTION_UPDATED

- OPTIMIZATION_STARTED

- OPTIMIZATION_PROGRESS

- OPTIMIZATION_COMPLETED

- SCENARIO_STARTED

- SCENARIO_PROGRESS

- SCENARIO_COMPLETED

- RECOMMENDATION_CREATED

- APPROVAL_CREATED

- SHIPMENT_STATUS_CHANGED

- MARKET_SHOCK_DETECTED

- MODEL_DRIFT_DETECTED

# **35. MLOps and Model Governance**

## **35.1 Model registry**

- Model ID and version

- Training/validation period

- Feature set

- Metrics

- Artifact location

- Deployment timestamp

- Owner/status

## **35.2 Monitoring**

- Forecast error

- Feature drift

- Prediction drift

- Data freshness

- Model confidence degradation

- Market regime change

## **35.3 Fallback**

```
Advanced sequence model
```

```
 ↓ fallback
XGBoost / LightGBM
 ↓ fallback
ARIMA / baseline
 ↓
Conservative forecast mode
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **36. Security and Governance**

## **36.1 Roles**

- ADMIN

- CHARTERING_MANAGER

- OPERATIONS

- COMMERCIAL

- LEADERSHIP

- VIEWER

## **36.2 Controls**

- Authentication and session management

- RBAC

- API authorization

- Approval authorization

- Secrets in environment/secret manager

- Audit logging

- No mutation of historical audit records

- Data classification: PUBLIC / INTERNAL / CONFIDENTIAL / SENSITIVE

# **37. Non-Functional Requirements**

| **Category**     | **Requirement**                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Performance      | Normal read APIs should be responsive; expensive jobs run<br>asynchronously.                                               |
| Scalability      | Support increasing vessels, ports, shipments and scenarios without<br>changing domain contracts.                           |
| Availability     | Target high availability for deployed service; exact SLA to be set for<br>production environment.                          |
| Reliability      | External data failure must not crash the full application.                                                                 |
| Reproducibility  | Forecast/optimization/scenario results must be reproducible from<br>stored state and seed when deterministic mode is used. |
| Observability    | Structured logs, request IDs, job status, metrics and health checks.                                                       |
| Security         | RBAC, secrets management, auditability.                                                                                    |
| Accessibility    | Readable contrast, keyboard focus, reduced motion, semantic<br>controls.                                                   |
| Maintainability  | Domain logic separated from API and frontend rendering.                                                                    |
| Data Integrity   | Units, timestamps, geographic felds and foreign-key relationships<br>validated.                                            |
| Explainability   | Recommendation lineage must be retrievable.                                                                                |
| Demo Reliability | Canonical SIH scenario must work without unstable external<br>dependencies.                                                |

# **38. Testing and Validation Strategy**

## **38.1 Unit tests**

- Cost formulas

- Compatibility rules

- Forecast transformations

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- Quantile calculations

- Risk metrics

- Inventory projections

- Scenario distributions

## **38.2 Integration tests**

Canonical pipeline: Create Shipment → State Snapshot → Forecast → Candidate Generation → Compatibility → Cost → Optimization → Recommendation.

## **38.3 E2E**

Canonical user journey including scenario shock, contract optimization, approval and audit.

## **38.4 ML validation**

- Walk-forward splits

- No leakage

- Holdout evaluation

- Prediction interval coverage

- Backtesting documentation

- Model version traceability

# **39. Synthetic Data and Demo Determinism**

Because SAIL internal datasets may not be available during SIH, the prototype must include a deterministic synthetic dataset. The supplied NAVISAIL design explicitly says to simulate SAIL-internal data when necessary and to identify synthetic/demo data clearly. [Source: supplied NAVISAIL design notes]

```
data/demo/
 ├── demo_market.csv
```

- `├── demo_vessels.csv`

- `├── demo_ports.csv`

- `├── demo_berths.csv`

- `├── demo_ais.csv`

- `├── demo_weather.csv`

- `├── demo_commodity.csv`

- `├── demo_fuel.csv`

- `├── demo_fx.csv`

- `├── demo_inventory.csv`

- `└── demo_contracts.csv`

Use a fixed demo seed such as 26006. The final UI must display SYNTHETIC or DEMO whenever such data is used.

# **40. SIH Demo Experience**

The demo should tell one continuous story, not a sequence of unrelated page clicks. The prior concept recommends starting with a 150,000 MT Australia-to-Bokaro shipment, showing a WAIT decision, explaining the drivers, selecting a vessel and port, then changing Paradip congestion/outage, re-optimizing and comparing contract strategies. [Source: supplied NAVISAIL design notes]

| **Time**  | **Demo action**     | **Judge-visible outcome**                     |
| --------- | ------------------- | --------------------------------------------- |
| 0:00-0:30 | Open Command Center | Executive maritime state and priority actions |
| 0:30-1:00 | Create shipment     | 150,000 MT Australia → Bokaro                 |
| 1:00-1:30 | Forecast            | Probabilistic freight and confdence           |
| 1:30-2:00 | Recommendation      | WAIT window + vessel + port + cost            |
| 2:00-2:30 | Explain             | Drivers and risks                             |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **Time**  | **Demo action**                | **Judge-visible outcome**                         |
| --------- | ------------------------------ | ------------------------------------------------- |
| 2:30-3:00 | Port/vessel inspection         | Compatibility and landed-cost comparison          |
| 3:00-3:40 | Trigger Paradip outage +5 days | Recommendation shifts through re-<br>optimization |
| 3:40-4:20 | Monte Carlo                    | P95/CVaR and laycan/stockout risk                 |
| 4:20-4:50 | Contract simulation            | Spot vs COA vs Hybrid                             |
| 4:50-5:00 | Copilot + approval             | Explain decision and show audit trail             |

### **Demo closing line**

NAVISAIL does not merely forecast freight. It converts maritime uncertainty into an explainable procurement decision.

# **41. Deployment and DevOps**

Use Docker Compose during development and a simple container deployment strategy for the SIH prototype. The submitted architecture lists AWS, Docker and GitHub Actions, which can remain the deployment direction while keeping the first prototype simple. [Source: supplied NAVISAIL design notes]

- Backend container

- Frontend container

- PostgreSQL/PostGIS

- Redis

- Background worker

- Object storage/local persistent volume

- CI/CD pipeline

## **41.1 Environments**

- development

- staging

- production/demo

# **42. Observability and Operations**

- API latency

- Worker execution time

- Forecast duration

- Optimization duration

- Scenario progress

- Data source health

- Model health

- Database health

- Redis health

- External connector failures

Use structured logs and correlation IDs so a recommendation can be traced across ingestion, state construction, model execution, optimization and response delivery.

# **43. Accessibility and Usability**

- Keyboard navigation and visible focus states

- Readable typography and sufficient contrast

- Tooltips for technical metrics

- Reduced-motion mode

- Clear status semantics

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

- Loading/skeleton/empty/error states

- Avoid reliance on color alone for risk status

- Descriptive labels for charts and controls

# **44. Risk Register**

| **Risk**                              | **Impact** | **Mitigation**                                                                   |
| ------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| Insuficient live data                 | High       | Use transparent synthetic/estimated data<br>plus source/freshness metadata.      |
| Forecast accuracy weak                | High       | Walk-forward validation, ensembles,<br>uncertainty bands, conservative fallback. |
| Optimizer returns infeasible plan     | Critical   | Hard constraints + feasibility tests +<br>alternative fallback.                  |
| LLM hallucination                     | High       | Tool-grounded copilot; prohibit unsupported<br>numerical claims.                 |
| 3D UI hurts performance               | Medium     | Lazy loading, reduced-motion, limit 3D to<br>decision-relevant views.            |
| External API outage                   | High       | Caching, last-known state, synthetic demo<br>mode, graceful degradation.         |
| Architecture over-complexity          | High       | Modular monolith frst; defer<br>microservices/Kafka/NiFi unless needed.          |
| Data leakage in forecasting           | Critical   | Time-aware splits and feature timestamp<br>controls.                             |
| Demo non-determinism                  | High       | Fixed seed and local canonical dataset.                                          |
| Unauthorized commercial action        | Critical   | RBAC + human approval + audit.                                                   |
| UI looks better than underlying logic | High       | Data-driven screens and end-to-end<br>integration gate before polish.            |

# **45. Team Workstreams**

| **Workstream**        | **Primary responsibilities**                                                           |
| --------------------- | -------------------------------------------------------------------------------------- |
| Data / ML             | data connectors, features, forecasting, confdence, drift                               |
| Maritime / OR         | AIS, vessel supply, port/berth, congestion, optimization, landed cost                  |
| Backend / Platform    | FastAPI, DB, APIs, events, workers, audit, security                                    |
| Frontend / Experience | command center, charts, maps, 3D, recommendation UX, copilot UX                        |
| Integration / Demo    | synthetic dataset, canonical scenario, end-to-end tests, demo<br>runbook, presentation |

# **46. Phase-by-Phase Implementation Roadmap**

| **Phase** | **Name**                                   | **Primary work**                                                                                                                           | **Gate**                                      |
| --------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| Phase 0   | Greenfeld Repository<br>Initialization     | Create clean repo foundation,<br>FastAPI/Next.js baseline,<br>PostgreSQL/PostGIS, Redis,<br>Docker, confguration, docs and<br>smoke tests. | Fresh clone initializes and runs<br>cleanly.  |
| Phase 1   | Engineering Conventions, CI and<br>Quality | Linting, formatting, typing,<br>testing, CI, quality gates,<br>conventions, dependency<br>discipline.                                      | Backend/frontend CI gates pass.               |
| Phase 2   | Domain Model and Database<br>Foundation    | Canonical entities, migrations,<br>repositories,PostGIS,schemas                                                                            | Zero-to-clean database<br>migration succeeds. |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **Phase** | **Name**                                   | **Primary work**<br>and reference seeds                                                                        | **Gate**                                                                   |
| --------- | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Phase 3   | Data Platform and Source<br>Contracts      | .<br>Source adapters, normalization,<br>quality, freshness, lineage and<br>common data contracts.              | All domains consume a common<br>source contract.                           |
| Phase 4   | Synthetic and Demo Data Engine             | Deterministic generators for<br>market, AIS, vessels, ports,<br>weather, fuel, FX, inventory and<br>contracts. | Fixed-seed dataset reproduces<br>exactly.                                  |
| Phase 5   | Maritime State Engine                      | Versioned MaritimeStateVector,<br>state assembly, snapshotting,<br>difingand eventpublication.                 | Downstream engines consume<br>canonical snapshots.                         |
| Phase 6   | AIS and Vessel Intelligence                | Track normalization, ETA,<br>availability, vessel supply and<br>candidategeneration.                           | Vessel candidates are queryable<br>with evidence.                          |
| Phase 7   | Port, Berth and Compatibility              | Physical/operational<br>compatibility rules and berth-<br>level feasibility.                                   | Infeasible vessel/port/berth<br>combinations are rejected with<br>reasons. |
| Phase 8   | Freight Forecasting V1                     | Historical features, baselines<br>and ML forecasting by route and<br>vessel class.                             | Backtested forecast API works<br>without leakage.                          |
| Phase 9   | Probabilistic Forecasting and<br>Confdence | Quantiles, intervals, calibration,<br>confdence and model<br>comparison.                                       | Forecasts expose uncertainty<br>and confdence.                             |
| Phase 10  | Port Congestion and Waiting<br>Prediction  | AIS/port state, waiting-time<br>estimation, queue signals and<br>congestion scenarios.                         | Congestion feeds ETA, cost and<br>recommendations.                         |
| Phase 11  | Landed Cost Engine                         | Freight, fuel, port, waiting,<br>demurrage, inland, FX, inventory<br>and disruption cost components.           | Every material cost component is<br>traceable.                             |
| Phase 12  | Optimization Core                          | OR-Tools models for vessel, port,<br>route, timing, allocation and<br>hard/soft constraints.                   | Feasible alternatives and best<br>solution are returned.                   |
| Phase 13  | Charter Now / Wait and Cost of<br>Waiting  | Booking-date comparison, future<br>market uncertainty,<br>delay/inventory exposure and<br>bookingwindow.       | Timing recommendation and<br>COW curve are reproducible.                   |
| Phase 14  | Contract Strategy Optimizer                | Spot, COA, time charter and<br>hybrid multi-voyage strategy<br>optimization.                                   | Strategy comparison integrates<br>cost, risk and fexibility.               |
| Phase 15  | Risk and Monte Carlo Engine                | Distributions, correlated<br>uncertainty, 10,000-scenario<br>baseline, P95/CVaR and<br>outcomeprobabilities.   | Deterministic scenario runs<br>produce stable risk metrics.                |
| Phase 16  | Market Regime and Shock<br>Detection       | Stable/rising/falling/volatile/<br>disrupted regimes and shock<br>detection.                                   | Regime/shock state alters<br>downstream policy<br>appropriately.           |
| Phase 17  | Digital Twin Core                          | Stateful vessel, voyage, port,<br>berth and plant simulation with<br>isolated what-if scenarios.               | Disruption propagates through<br>ETA, cost and inventory.                  |
| Phase 18  | Plant Inventory and Supply Risk            | Stock projection, days of cover,<br>safety stock and stockout<br>probability.                                  | Inventory risk can materially<br>change decisions.                         |
| Phase 19  | Unifed Recommendation Engine               | End-to-end numerical decision<br>pipeline and canonical<br>recommendation object.                              | One reproducible decision is<br>returned.                                  |
| Phase 20  | Explainability and Decision<br>Memo        | Factors, assumptions,<br>counterfactuals, evidence,<br>confdence and structured<br>decision note.              | Recommendation explains WHY<br>and WHAT COULD GO WRONG.                    |
| Phase 21  | Copilot Tool Interface                     | Typed tool interfaces for domain<br>retrieval, calculations,<br>simulation and explanation.                    | Copilot can answer through<br>grounded tools only.                         |
| Phase 22  | Bounded Dynamic Agent<br>Orchestration     | Dynamic agents for task<br>decomposition, tool planning,<br>context sharing,recoveryand                        | Agent layer cannot bypass<br>numerical or approval<br>boundaries.          |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **Phase** | **Name**                                     | **Primary work**<br>bdd fti                                                                                  | **Gate**                                                               |
| --------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| Phase 23  | Human Approval, Execution and<br>Audit       | oune reecon.<br>Approval state machine,<br>controlled execution, actuals<br>and immutable audit lineage.     | Commercial actions require<br>human authorization and<br>traceability. |
| Phase 24  | Frontend Design System                       | Design tokens, glass surfaces,<br>data components, maps,<br>accessibility and interaction<br>primitives.     | All screens share one design<br>system.                                |
| Phase 25  | Command Center UI                            | Executive cockpit, maritime<br>state, alerts, savings, risks,<br>active decisions and data health.           | Command Center is fully data-<br>driven.                               |
| Phase 26  | Freight Intelligence UI                      | Historical/forecast charts,<br>uncertainty bands, horizons,<br>COW and regime intelligence.                  | Interactive forecast workfow is<br>functional.                         |
| Phase 27  | Shipment Planner UI                          | Create/validate shipment,<br>decision session, constraints<br>and analysis initiation.                       | Shipment creates a persistent<br>decision session.                     |
| Phase 28  | Recommendation UI                            | Hero recommendation,<br>vessel/port/route/contract,<br>costs, risk, confdence,<br>alternatives and approval. | Decision is understandable at a<br>glance.                             |
| Phase 29  | Port Digital Twin UI                         | Map/3D port state, berth cards,<br>vessel inspector, compatibility<br>and congestion.                        | Physical and commercial state<br>are linked.                           |
| Phase 30  | Contract Simulator UI                        | Spot/COA/time charter/hybrid<br>sliders, allocations, cost/risk<br>comparison.                               | Contract results are live from<br>backend models.                      |
| Phase 31  | Risk and What-if UI                          | Scenario controls, distributions<br>and side-by-side baseline vs<br>scenario impact.                         | Shock changes propagate<br>without mutating baseline.                  |
| Phase 32  | Copilot UI                                   | Streaming grounded<br>conversation, tool activity,<br>sources and decision-session<br>context.               | Copilot is transparent and tool-<br>grounded.                          |
| Phase 33  | Execution and Audit UI                       | Approval controls, workfow<br>timeline, plan-vs-actual and<br>audit inspection.                              | Operational handof and<br>traceability are visible.                    |
| Phase 34  | Realtime Events and Unifed<br>Frontend State | SSE, event reducers,<br>reconnection, decision-session<br>synchronization.                                   | All pages refect the same live<br>session state.                       |
| Phase 35  | 3D and Spatial Experience                    | Decision-relevant<br>vessel/route/port/twin 3D with<br>performance fallbacks.                                | 3D improves comprehension<br>without becoming decoration.              |
| Phase 36  | Security and RBAC Hardening                  | Authentication, roles,<br>permissions, secure actions,<br>session and audit hardening.                       | Unauthorized actions are<br>blocked server-side.                       |
| Phase 37  | MLOps and Model Governance                   | Model registry, validation,<br>monitoring, drift, fallback and<br>promotion controls.                        | Model health and lineage are<br>observable.                            |
| Phase 38  | Full System Integration and<br>Hardening     | Complete orchestration, retries,<br>idempotency, partial failure<br>handling and integration<br>consistency. | One end-to-end request<br>executes reliably.                           |
| Phase 39  | Performance and Resilience                   | Caching, background jobs, DB<br>tuning, runtime protection and<br>graceful degradation.                      | Performance and failure tests<br>pass.                                 |
| Phase 40  | Comprehensive Validation                     | Unit, integration, API, E2E,<br>optimization, ML, simulation,<br>securityand realtime validation.            | Critical path passes the full test<br>matrix.                          |
| Phase 41  | SIH Deterministic Demo Package               | Canonical 150,000 MT Australia-<br>to-Bokaro scenario, shock<br>scenarios, seeded data and<br>runbook.       | Demo repeats reliably from a<br>clean environment.                     |
| Phase 42  | Deployment, Observability and<br>Operations  | Container deployment, health,<br>metrics,logging, jobs,backups                                               | Fresh environment is deployable<br>and diagnosable.                    |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **Phase** | **Name**                               | **Primary work**                                                                                               | **Gate**                                             |
| --------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
|           |                                        | and operational runbooks.                                                                                      |                                                      |
| Phase 43  | UX, Accessibility and Visual<br>Polish | Typography, spacing, motion,<br>loading/error states, keyboard<br>support, contrast and premium<br>fnish.      | Premium UX passes<br>usability/accessibility review. |
| Phase 44  | SIH Traceability and Final Audit       | PRD-to-code-to-test-to-demo<br>mapping, security/data/ML/UX<br>audit andgapclosure.                            | No critical requirement is<br>unmapped.              |
| Phase 45  | Final Release Candidate                | Clean-clone validation, frozen<br>demo confguration, regression,<br>fnal documentation and release<br>package. | NAVISAIL AI v1.1-SIH release<br>candidate approved.  |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **46A. Master Coding-Agent Prompt Template**

```
You are implementing NAVISAIL AI, an SIH 2026 maritime procurement and chartering decision-support
platform for SAIL.
```

```
Core principle:
```

```
Predict → Simulate → Optimize → Decide.
```

```
Architecture rules:
```

- `Preserve domain boundaries.`

- `Do not replace deterministic calculations with LLM guesses.`

- `Use MaritimeStateVector as the shared state between data and intelligence engines.`

- `Keep Dynamic Agent V2 as an orchestration layer, not numerical truth.`

- `All major entities use typed schemas.`

- `All business calculations are server-side and testable.`

- `UI consumes APIs; do not hard-code business values.`

- `All recommendations are auditable.`

- `Explicitly mark LIVE/DELAYED/ESTIMATED/SYNTHETIC data.`

- `Prefer modular monolith + workers over premature microservices.`

- `Do not delete working features without evidence.`

- `Inspect current code before modifying it.`

```
For the requested phase:
```

`1. Inspect all impacted code.`

`2. Identify dependencies and current behavior.`

`3. Implement the phase completely.`

`4. Add/update schemas, migrations, APIs and tests as necessary.`

`5. Integrate with existing state/event infrastructure.`

`6. Document decisions and assumptions.`

`7. Run lint/type-check/tests.`

`8. Report files changed, APIs added, tests run, known limitations, and exact definition-of-done status.`

`9. Do not proceed to future-phase features unless required as a dependency.`

`10. Never fabricate production numbers. Use deterministic synthetic data in DEMO mode where necessary.`

# **47. Definition of Done Framework**

| **Gate**       | **Defnition**                                               |
| -------------- | ----------------------------------------------------------- |
| Code           | No lint/type errors; critical tests passing.                |
| Data           | Schema/version/freshness/quality documented.                |
| API            | Typed request/response; validation and error cases covered. |
| Business logic | Unit tests cover calculation and edge cases.                |
| Integration    | Feature afects shared decision state correctly.             |
| UI             | Loading/error/empty/accessible states implemented.          |
| Observability  | Logs/events/metrics exist for meaningful jobs.              |
| Audit          | Relevant decisions and versions persisted.                  |
| Demo           | Canonical scenario reproduces expected behavior.            |
| Documentation  | Relevant README/API/design notes updated.                   |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **48. Acceptance Criteria**

- AC-01: User can create a shipment with commodity, quantity, origin, destination plant, required date and risk tolerance.

- AC-02: NAVISAIL can build a maritime state snapshot for the shipment.

- AC-03: Freight forecast returns multiple horizons and uncertainty intervals.

- AC-04: Forecast confidence is explainable and not an arbitrary hard-coded number.

- AC-05: Candidate vessels are filtered for availability and physical suitability.

- AC-06: Port/berth compatibility returns reasons for rejection.

- AC-07: Landed cost includes ocean, bunker, port, waiting, demurrage, handling, inland and risk components.

- AC-08: Optimizer returns feasible alternatives and a best solution.

- AC-09: Charter Now/Wait returns a booking recommendation and Cost-of-Waiting curve.

- AC-10: Contract optimizer compares spot/COA/time-charter/hybrid.

- AC-11: Monte Carlo produces cost/risk distributions and P95/CVaR.

- AC-12: Digital twin propagates a port disruption to downstream timing/cost/inventory.

- AC-13: Inventory state affects optimization when stockout risk is material.

- AC-14: Recommendation exposes WHY, risks, alternatives and confidence.

- AC-15: Copilot answers numerical questions only through tool-backed results.

- AC-16: AI cannot approve or execute a commercial decision without human authorization.

- AC-17: Recommendation and approval are auditable.

- AC-18: Seven main UI screens share one decision session.

- AC-19: Demo works reproducibly in DEMO mode.

- AC-20: The system degrades gracefully if a non-critical external source fails.

# **49. KPIs and Measurement**

| **KPI**                                       | **Defnition**                                               | **Use**               |
| --------------------------------------------- | ----------------------------------------------------------- | --------------------- |
| Forecast MAE                                  | mean absolute forecast error                                | model quality         |
| Interval coverage                             | actuals inside predicted interval                           | uncertainty quality   |
| Decision Savings                              | baseline cost minus NAVISAIL cost                           | business value        |
| P95 cost reduction                            | baseline P95 minus recommended P95                          | risk beneft           |
| Laycan probability                            | probability shipment meets required window                  | schedule reliability  |
| Stockout probability                          | simulated probability of supply shortfall                   | plant risk            |
| Manual analysis time                          | time from request to decision pack                          | decision speed        |
| Optimization feasibility rate                 | share of runs with feasible solutions                       | optimizer reliability |
| Recommendation explainability<br>completeness | share of recommendations with factor +<br>lineage + risks   | governance            |
| Data freshness coverage                       | share of critical features with valid freshness<br>metadata | data trust            |
| Plan-vs-actual deviation                      | diference between forecast/plan and actual                  | feedback quality      |

# **50. Future Roadmap**

- Real production AIS streams and higher-frequency state updates.

- Expanded origin/commodity intelligence.

- Learned berth/port turnaround models using larger datasets.

- Dynamic portfolio optimization across multiple simultaneous shipments.

- Contract negotiation support and bid analysis.

- More advanced route/weather uncertainty modeling.

- Human feedback as a structured learning signal.

- Automated model retraining pipelines with approval gates.

- Enterprise integrations with procurement/ERP/logistics systems.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

 Broader maritime digital-twin coverage across SAIL operations.

# **51. Appendix A — Final Repository Structure**

```
navisail-ai/
├── README.md
├── LICENSE
├── Makefile
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── package.json
├── pnpm-workspace.yaml
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── ml/
│   ├── domain/
│   ├── demo/
│   └── sih/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── data/
│   │   ├── maritime/
```

```
│   │   ├── forecasting/
```

```
│   │   ├── congestion/
```

```
│   │   ├── optimization/
```

```
│   │   ├── risk/
```

```
│   │   ├── digital_twin/
│   │   ├── recommendations/
│   │   ├── copilot/
```

```
│   │   ├── events/
```

```
│   │   └── mlops/
│   └── tests/
│
├── frontend/
```

```
│   ├── app/
```

```
│   ├── components/
```

```
│   ├── three/
```

```
│   ├── state/
```

```
│   ├── hooks/
```

```
│   ├── lib/
```

```
│   ├── types/
```

```
│   └── styles/
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
│
├── dynamic_agents/
│   ├── graph/
│   ├── meta/
│   ├── factory/
│   ├── runtime/
│   ├── registry/
│   ├── reflection/
│   └── shared/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   ├── demo/
│   └── dictionaries/
│
├── models/
│   ├── forecast/
│   ├── congestion/
│   └── registry/
│
├── simulation/
│   ├── scenarios/
│   ├── distributions/
│   └── monte_carlo/
│
├── infrastructure/
│   ├── docker/
│   ├── postgres/
│   ├── redis/
│   └── deployment/
│
├── scripts/
│   ├── seed_demo.py
│   ├── train_forecast.py
│   ├── generate_ais.py
│   ├── run_scenario.py
│   └── evaluate_models.py
│
└── .github/workflows/
    ├── test.yml
    ├── build.yml
    └── deploy.yml
```

# **52. Appendix B — Canonical Data Objects**

## **52.1 Shipment**

```
{
```

```
  "shipment_id": "AUS-CC-1027",
```

```
  "commodity": "PREMIUM_HARD_COKING_COAL",
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
  "quantity_mt": 150000,
  "origin": "HAY_POINT",
  "destination_plant": "BOKARO",
  "required_by": "2027-01-15",
  "risk_tolerance": "MEDIUM",
  "contract_preference": "FLEXIBLE"
}
```

## **52.2 Vessel**

```
{
  "imo": "1234567",
  "name": "MV EXAMPLE",
  "class": "PANAMAX",
  "dwt": 82400,
  "loa_m": 228,
  "beam_m": 32,
  "draft_m": 14.2,
  "speed_knots": 13.5,
  "fuel_mt_day": 28
}
```

## **52.3 Maritime State Vector**

```
{
  "timestamp": "...",
  "market": {...},
  "freight": {...},
  "vessel_supply": {...},
  "ports": {...},
  "weather": {...},
  "commodity": {...},
  "fuel": {...},
  "fx": {...},
  "geopolitics": {...},
  "market_regime": "NORMAL",
  "data_quality": {...}
}
```

## **52.4 Recommendation**

```
{
  "action": "WAIT",
  "wait_days": 9,
  "vessel_strategy": "2_PANAMAX",
  "port": "PARADIP",
  "contract": "HYBRID",
  "expected_cost": 11.06,
  "p95_cost": 12.14,
  "expected_saving": 4.73,
  "forecast_confidence": 0.84,
  "decision_confidence": 0.81,
  "reason_codes": [
    "FREIGHT_DECLINING",
```

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

```
    "VESSEL_SUPPLY_IMPROVING",
```

```
}
```

```
    "PORT_CONGESTION_STABLE"
```

```
  ]
```

# **53. Appendix C — API Catalog**

| **Endpoint**                          | **Purpose**                                                 |
| ------------------------------------- | ----------------------------------------------------------- |
| POST /api/v1/shipments                | Create shipment and initialize decision session.            |
| GET /api/v1/maritime-state            | Return latest fused maritime state.                         |
| GET /api/v1/forecast                  | Return forecast and uncertainty for route/class/horizon.    |
| GET /api/v1/vessels/candidates        | Return vessels meeting candidate criteria.                  |
| POST /api/v1/compatibility/check      | Evaluate vessel/berth physical and operational feasibility. |
| GET /api/v1/congestion/{port_id}      | Return current/predicted port congestion.                   |
| POST /api/v1/cost/estimate            | Return landed-cost decomposition.                           |
| POST /api/v1/optimization/charter     | Run end-to-end charter optimization.                        |
| POST /api/v1/contracts/optimize       | Optimize spot/COA/time charter/hybrid structure.            |
| POST /api/v1/scenarios/run            | Start Monte Carlo/what-if simulation.                       |
| GET /api/v1/scenarios/{id}/progress   | Stream/return scenario progress.                            |
| POST /api/v1/digital-twin/simulate    | Run digital-twin state propagation.                         |
| GET /api/v1/recommendations/{id}      | Return canonical recommendation.                            |
| POST /api/v1/copilot/query            | Run tool-grounded natural-language query.                   |
| POST /api/v1/copilot/decision-note    | Generate structured decision note.                          |
| POST /api/v1/approvals/{id}/approve   | Approve recommendation.                                     |
| GET /api/v1/execution/{shipment_id}   | Return execution status/timeline.                           |
| GET /api/v1/audit/{recommendation_id} | Return decision lineage.                                    |

# **54. Appendix D — Research and Source Basis**

The SIH submission includes the following references as research basis. The list is reproduced here as a project reference index rather than as a claim that each source has been independently re-verified for this PRD.

- F. Kjeldsberg, Z. H. Munim, and H.-J. Schramm, “Machine learning in freight rate forecasting: A systematic literature review,” Maritime Economics & Logistics, 2026.

- J. Wu, Q. Fang, Y. Ji, and Y. Zhang, “Forecasting dry bulk freight index for maritime decision-making,” Applied Mathematical Modelling, 2026.

- N. Kim, J. Cha, and J. Jeon, “A comparative evaluation of machine learning approaches for container freight rates prediction,” Asian Journal of Shipping and Logistics, 2025.

- Q. Sun, Q. Meng, and M. C. Chou, “Optimizing voyage charterparty arrangement: Laytime negotiation and operations coordination,” European Journal of Operational Research, 2021.

- W. Peng et al., “A deep learning approach for port congestion estimation and prediction,” Maritime Policy & Management, 2023.

- T. Zhang et al., “Prediction of container port congestion status and its impact on ship’s time in port based on AIS data,” Maritime Policy & Management, 2024.

- M.-H. Choi and W. Yoon, “Predicting ship waiting times using machine learning for enhanced port operations,” IEEE Access, 2025.

- F. Mauro and A. A. Kana, “Digital twin for ship life-cycle: A critical systematic review,” Ocean Engineering, 2023.

- J.-H. Lee et al., “Real-time digital twin for ship operation in waves,” Ocean Engineering, 2022.

- O. K. Kinaci, “Ship digital twin architecture for optimizing sailing automation,” Ocean Engineering, 2023.

The supplied SIH PDF is six pages and explicitly contains sections for Technical Approach, Feasibility and Viability, Impact and Benefit, and Novelty/Research. [Source: supplied NAVISAIL design notes]

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **Final Product North Star**

### **NAVISAIL AI**

Predict → Simulate → Optimize → Decide

The platform is complete when a user can submit a real-world cargo requirement and NAVISAIL can produce a reproducible, physically feasible, risk-adjusted and explainable chartering/procurement recommendation; when a scenario changes, the system recomputes the downstream decision coherently; when a human approves the recommendation, the resulting action is auditable; and when the voyage completes, actual outcomes can be compared against the original plan to improve future decisions.

The strongest positioning from the prior NAVISAIL work is: “NAVISAIL transforms freight forecasting into an explainable, risk-aware chartering decision. It jointly optimizes market-entry timing, vessel class, berth-compatible destination port and spot-versus-multi-voyage contracting to minimize SAIL’s total landed logistics cost.” [Source: supplied NAVISAIL design notes]

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **55. Appendix E — Functional Requirement Catalog**

The following requirements convert the product intent into implementation-testable statements. IDs are stable identifiers for engineering, QA, traceability and SIH review. Each requirement is classified as Critical, High or Medium based on its effect on the core decision journey.

| **ID**<br>FR-001 | **Area**<br>Shipment | **Requirement**<br>Create shipment with commodity,<br>quantity, origin, destination plant,<br>required date and risk tolerance.<br> | **Priority**<br>High |
| ---------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| FR-002           | Shipment             | Validate shipment quantities,<br>dates, identifers and mandatory<br>felds.                                                          | High                 |
| FR-003           | Shipment             | Create a persistent decision<br>session when analysis begins.                                                                       | High                 |
| FR-004           | Shipment             | Persist shipment revisions without<br>losing prior decision snapshots.                                                              | High                 |
| FR-005           | Shipment             | Support laycan and scheduling<br>constraints.                                                                                       | High                 |
| FR-006           | Shipment             | Support shipment priority and<br>decision status.                                                                                   | High                 |
| FR-007           | Data                 | Normalize data from fle, synthetic<br>and external connectors into<br>common contracts.                                             | High                 |
| FR-008           | Data                 | Record source, observed time,<br>ingestion time, quality, freshness<br>and status.                                                  | High                 |
| FR-009           | Data                 | Reject or quarantine invalid records<br>usingexplicit validation outcomes.                                                          | High                 |
| FR-010           | Data                 | Track transformation and lineage<br>metadata.                                                                                       | High                 |
| FR-011           | Data                 | Expose data-source health and<br>freshness to users.                                                                                | High                 |
| FR-012           | Data                 | Never represent synthetic/demo<br>values as LIVE.                                                                                   | High                 |
| FR-013           | Maritime State       | Create versioned<br>MaritimeStateVector snapshots.                                                                                  | High                 |
| FR-014           | Maritime State       | Make state reproducible for a given<br>decision session.                                                                            | High                 |
| FR-015           | Maritime State       | Support state difing and material-<br>change detection.                                                                             | High                 |
| FR-016           | Maritime State       | Expose state metadata to<br>downstream engines and audit.                                                                           | Critical             |
| FR-017           | Vessel/AIS           | Normalize AIS positions and vessel<br>attributes.                                                                                   | High                 |
| FR-018           | Vessel/AIS           | Track vessel movement history.<br>                                                                                                  | High                 |
| FR-019           | Vessel/AIS           | Estimate ETA with explicit<br>assumptions.                                                                                          | High                 |
| FR-020           | Vessel/AIS           | Estimate vessel availability from<br>operational state and timing.                                                                  | High                 |
| FR-021           | Vessel/AIS           | Generate vessel candidates for a<br>shipment.                                                                                       | High                 |
| FR-022           | Vessel/AIS           | Return confdence and freshness<br>with vessel intelligence.                                                                         | High                 |
| FR-023           | Port/Berth           | Represent port and berth technical<br>constraints.                                                                                  | High                 |
| FR-024           | Port/Berth           | Evaluate vessel-port compatibility.                                                                                                 | Critical             |
| FR-025           | Port/Berth           | Evaluate vessel-berth<br>compatibility.                                                                                             | High                 |
| FR-026           | Port/Berth           | Separate hard feasibility failures<br>from softpenalties.                                                                           | High                 |
| FR-027           | Port/Berth           | Explain the limiting compatibility<br>factor.                                                                                       | High                 |
| FR-028           | Port/Berth           | Support dynamic<br>closure/weather/operational<br>constraints.                                                                      | Critical             |
| FR-029           | Forecasting          | Generate route/vessel-class<br>forecasts at 7/15/30/90-day<br>horizons.                                                             | High                 |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **ID**<br>FR-030 | **Area**<br>Forecasting | **Requirement**<br>Benchmark predictive models<br>against naive baselines.                                      | **Priority**<br>High |
| ---------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------- |
| FR-031           | Forecasting             | Prevent time leakage in feature<br>construction and validation.                                                 | High                 |
| FR-032           | Forecasting             | Produce prediction<br>intervals/quantiles.<br>                                                                  | High                 |
| FR-033           | Forecasting             | Expose forecast confdence<br>separately from decision<br>confdence.                                             | High                 |
| FR-034           | Forecasting             | Record model and training<br>metadata.                                                                          | High                 |
| FR-035           | Congestion              | Estimate port congestion for a time<br>window.                                                                  | High                 |
| FR-036           | Congestion              | Estimate waitingtime distributions.                                                                             | High                 |
| FR-037           | Congestion              | Make congestion available to ETA<br>and landed cost.                                                            | High                 |
| FR-038           | Congestion              | Support disruption/outage<br>scenarios.                                                                         | High                 |
| FR-039           | Landed Cost             | Calculate decomposed landed<br>logistics cost.                                                                  | High                 |
| FR-040           | Landed Cost             | Support freight, fuel, port, waiting,<br>demurrage, inland, FX and<br>inventory components where<br>applicable. | High                 |
| FR-041           | Landed Cost             | Store assumptions and units for<br>each cost component.                                                         | High                 |
| FR-042           | Landed Cost             | Calculate cost per tonne and total<br>voyage cost.                                                              | High                 |
| FR-043           | Landed Cost             | Produce risk-adjusted cost from<br>scenario outputs.                                                            | High                 |
| FR-044           | Optimization            | Represent decision variables, hard<br>constraints, soft constraints and<br>objectives.                          | High                 |
| FR-045           | Optimization            | Return feasible alternatives.                                                                                   | High                 |
| FR-046           | Optimization            | Return best solution with solver<br>status.                                                                     | High                 |
| FR-047           | Optimization            | Explain binding constraints and<br>penalties.                                                                   | High                 |
| FR-048           | Optimization            | Return an explicit infeasible result<br>when no solution exists.                                                | High                 |
| FR-049           | Charter Timing          | Compare booking now versus<br>future bookingwindows.                                                            | High                 |
| FR-050           | Charter Timing          | Use probabilistic freight rather than<br>point forecast alone.                                                  | High                 |
| FR-051           | Charter Timing          | Account for vessel availability risk<br>in waitingdecisions.                                                    | High                 |
| FR-052           | Charter Timing          | Account for delay and inventory<br>exposure.                                                                    | High                 |
| FR-053           | Charter Timing          | Return a booking window and Cost-<br>of-Waitingcurve.                                                           | High                 |
| FR-054           | Contracts               | Compare Spot, COA, Time Charter<br>and Hybrid strategies.                                                       | High                 |
| FR-055           | Contracts               | <br>Support multi-voyage allocation.                                                                            | High                 |
| FR-056           | Contracts               | Compare expected, tail-risk and<br>fexibilityoutcomes.                                                          | High                 |
| FR-057           | Contracts               | Expose strategy assumptions and<br>volume shares.                                                               | High                 |
| FR-058           | Risk/Simulation         | Run deterministic seeded Monte<br>Carlo simulations.                                                            | High                 |
| FR-059           | Risk/Simulation         | Return mean and percentile cost<br>metrics.                                                                     | High                 |
| FR-060           | Risk/Simulation         | Return P95/CVaR and relevant<br>probabilitymeasures.                                                            | High                 |
| FR-061           | Risk/Simulation         | Support freight, fuel, congestion,<br>weather, FX and vessel disruptions.                                       | High                 |
| FR-062           | Risk/Simulation         | Compare strategies under the<br>same random seed and scenario<br>                                               | High                 |
| FR-063           | Regime/Shocks           | set.<br>Classifymarket regime.                                                                                  | High                 |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **ID**<br>FR-064 | **Area**<br>Regime/Shocks | **Requirement**<br>Detect abnormal market or<br>operational shocks.                                                                   | **Priority**<br>High |
| ---------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| FR-065           | Regime/Shocks             | Expose shock severity and<br>evidence.                                                                                                | High                 |
| FR-066           | Regime/Shocks             | Allow regime/shock state to<br>infuence downstreampolicies.<br>                                                                       | High                 |
| FR-067           | Digital Twin              | Represent<br>shipment/vessel/port/berth/route/<br>plant state.                                                                        | High                 |
| FR-068           | Digital Twin              | Simulate voyage andport events.                                                                                                       | High                 |
| FR-069           | Digital Twin              | Clone baseline state for what-if<br>analysis.                                                                                         | High                 |
| FR-070           | Digital Twin              | Propagate disruptions into ETA,<br>cost and inventory.                                                                                | High                 |
| FR-071           | Inventory                 | Projectplant inventoryover time.                                                                                                      | High                 |
| FR-072           | Inventory                 | Calculate days of cover.                                                                                                              | High                 |
| FR-073           | Inventory                 | Calculate stockout probability<br>under scenarios.                                                                                    | High                 |
| FR-074           | Inventory                 | Expose inventory constraints to<br>optimization.                                                                                      | High                 |
| FR-075           | Recommendation            | Create one canonical<br>recommendation object.                                                                                        | High                 |
| FR-076           | Recommendation            | Rank alternatives using numerical<br>engine outputs.                                                                                  | High                 |
| FR-077           | Recommendation            | Include vessel, port, berth, route,<br>timingand contract strategy.                                                                   | High                 |
| FR-078           | Recommendation            | Include expected cost, P95/CVaR,<br>savings and supplyrisk.<br>                                                                       | High                 |
| FR-079           | Recommendation            | Include confdence, assumptions<br>and state snapshot reference.                                                                       | High                 |
| FR-080           | Explainability            | Explain why the recommendation<br>was selected.                                                                                       | High                 |
| FR-081           | Explainability            | Explain why a candidate was<br>rejected.                                                                                              | High                 |
| FR-082           | Explainability            | Provide counterfactual impact<br>where calculable.                                                                                    | High                 |
| FR-083           | Explainability            | List data/model/constraint<br>weaknesses.                                                                                             | High                 |
| FR-084           | Explainability            | Generate structured decision<br>memo.                                                                                                 | High                 |
| FR-085           | Copilot/Agents            | Expose approved NAVISAIL tools to<br>the copilot.                                                                                     | High                 |
| FR-086           | Copilot/Agents            | Ground numerical answers in tool<br>outputs.                                                                                          | High                 |
| FR-087           | Copilot/Agents            | Show tool execution/context when<br>appropriate.                                                                                      | High                 |
| FR-088           | Copilot/Agents            | Bound dynamic agent creation and<br>tool usage.                                                                                       | High                 |
| FR-089           | Copilot/Agents            | Prevent agents from approving or<br>executingcommercial action.                                                                       | High                 |
| FR-090           | Approval/Execution/Audit  | Require human authorization for<br>commercial action.                                                                                 | High                 |
| FR-091           | Approval/Execution/Audit  | Support approve/reject/modify with<br>identity, timestampand reason.                                                                  | High                 |
| FR-092           | Approval/Execution/Audit  | Track execution status through<br>operational lifecycle.                                                                              | Critical             |
| FR-093           | Approval/Execution/Audit  | Store recommendation, decision<br>and actual outcome lineage.                                                                         | High                 |
| FR-094           | Approval/Execution/Audit  | Prevent mutation of historical audit<br>records.                                                                                      | High                 |
| FR-095           | Frontend                  | Maintain a shared decision-session<br>context across major screens.                                                                   | Medium               |
| FR-096           | Frontend                  | Provide Command Center, Freight,<br>Shipment, Recommendation, Port<br>Twin, Contract, Risk, Copilot,<br>Execution and Audit surfaces. | Medium               |
| FR-097           | Frontend                  | Display<br>LIVE/DELAYED/ESTIMATED/SYNTH<br>ETIC/DEMO status clearly.                                                                  | Medium               |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **ID**<br>FR-098 | **Area**<br>Frontend | **Requirement**<br>Keep business calculations out of<br>React components. | **Priority**<br>Medium |
| ---------------- | -------------------- | ------------------------------------------------------------------------- | ---------------------- |
| FR-099           | Frontend             | Provide loading, empty, error and<br>partial-result states.               | Medium                 |
| FR-100           | Realtime             | Publish typed domain<br>progress/events.                                  | Medium                 |
| FR-101           | Realtime             | Provide SSE for long-running<br>analysis.                                 | Medium                 |
| FR-102           | Realtime             | Handle disconnect/reconnect<br>safely.                                    | Medium                 |
| FR-103           | Realtime             | Prevent duplicate event<br>application.                                   | Medium                 |
| FR-104           | MLOps                | Register model versions and<br>artifacts.                                 | High                   |
| FR-105           | MLOps                | Track feature/training/evaluation<br>metadata.                            | High                   |
| FR-106           | MLOps                | Monitor forecast/model drift.                                             | High                   |
| FR-107           | MLOps                | Provide conservative fallback<br>models.                                  | High                   |
| FR-108           | Demo                 | Provide deterministic canonical<br>SIH demo data.                         | High                   |
| FR-109           | Demo                 | Support 150,000 MT Australia-to-<br>Bokaro scenario.                      | High                   |
| FR-110           | Demo                 | Support Paradip disruption/shock<br>scenario.                             | High                   |
| FR-111           | Demo                 | Provide repeatable 5-minute<br>narrative fow.                             | High                   |
| FR-112           | Demo                 | Provide clean-environment demo<br>reset.                                  | High                   |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **56. Appendix F — Non-Functional Requirement Catalog**

| **ID**<br>NFR-001 | **Category**<br>Performance | **Requirement**<br>Normal read-only APIs should<br>remain responsive under expected<br>prototype load.                                          | **Target / Validation**<br>Defne and validate percentile<br>targets during Phase 39. |
| ----------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| NFR-002           | Performance                 | Expensive forecast, optimization,<br>Monte Carlo and simulation<br>operations must run<br>asynchronously.                                       | No long blocking request path.                                                       |
| NFR-003           | Performance                 | Frontend must not render large 3D<br>scenes before needed.                                                                                      | Lazy-load decision-relevant 3D.                                                      |
| NFR-004           | Scalability                 | Domain contracts must remain<br>valid as vessel, port, shipment and<br>scenario countsgrow.                                                     | No contract rewrite for scale.                                                       |
| NFR-005           | Reliability                 | Noncritical external data-source<br>failures must not crash the full<br>application.                                                            | Graceful degradation.                                                                |
| NFR-006           | Reliability                 | Critical decision dependencies<br>must fail closed rather than<br>inventingvalues.                                                              | Recommendation blocked when<br>critical truth is missing.                            |
| NFR-007           | Reproducibility             | Forecast, optimization and<br>simulation results must be<br>reproducible from stored inputs<br>and seed where deterministic<br>mode is enabled. | Deterministic regression tests.                                                      |
| NFR-008           | Data Integrity              | Timestamps must be timezone-<br>aware and normalized to UTC<br>internally.                                                                      | Database/API validation.                                                             |
| NFR-009           | Data Integrity              | Units and ranges must be explicitly<br>validated.                                                                                               | Reject invalid physical/business<br>values.                                          |
| NFR-010           | Data Integrity              | Foreign keys and geospatial<br>relationships must be enforced.                                                                                  | Database constraints.                                                                |
| NFR-011           | Security                    | Commercial actions require server-<br>side authorization.                                                                                       | RBAC and approval gate.                                                              |
| NFR-012           | Security                    | Secrets must never be committed<br>or exposed to the frontend.                                                                                  | Environment/secret manager.                                                          |
| NFR-013           | Security                    | Historical audit records must be<br>immutable.                                                                                                  | Append-only semantics.                                                               |
| NFR-014           | Observability               | Requests must carry<br>correlation/request identifers.                                                                                          | Structured logs.                                                                     |
| NFR-015           | Observability               | Workers and long-running jobs<br>must exposeprogress and status.                                                                                | Job status API/events.                                                               |
| NFR-016           | Observability               | Data-source health and freshness<br>must be visible to operators.                                                                               | Data health endpoints/UI.                                                            |
| NFR-017           | Maintainability             | Domain logic must remain outside<br>API route handlers.                                                                                         | Architecture tests/code review.                                                      |
| NFR-018           | Maintainability             | Frontend business calculations<br>must live in backend/domain<br>services.                                                                      | Frontend rule.                                                                       |
| NFR-019           | ML Governance               | Training/evaluation must use<br>chronological/time-aware<br>validation for time-series models.                                                  | No random split for primary<br>temporal evaluation.                                  |
| NFR-020           | ML Governance               | Every production/demo forecast<br>must identify its model version and<br>input state.                                                           | Model lineage.                                                                       |
| NFR-021           | Explainability              | Every material recommendation<br>must retain evidence, assumptions<br>and lineage.                                                              | Audit retrieval.                                                                     |
| NFR-022           | Accessibility               | Primary interactions must be<br>keyboard accessible and maintain<br>visible focus.                                                              | Accessibility review.                                                                |
| NFR-023           | Accessibility               | Risk and status cannot be<br>communicated through color<br>alone.                                                                               | Text/icons/labels required.                                                          |
| NFR-024           | Accessibility               | Reduced-motion behavior must be<br>supported.                                                                                                   | Motion preference handling.                                                          |
| NFR-025           | Demo Reliability            | The canonical demo must function<br>without unstable live feeds.                                                                                | Local deterministic dataset.                                                         |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **ID**<br>NFR-026 | **Category**<br>Demo Honesty | **Requirement**<br>Synthetic/demo data must be<br>visiblylabeled.                               | **Target / Validation**<br>UI/API data-status contract. |
| ----------------- | ---------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| NFR-027           | API Consistency              | All APIs must return typed,<br>versioned contracts and stable<br>error semantics.               | OpenAPI + schema tests.                                 |
| NFR-028           | Deployment                   | A fresh environment must be<br>reconstructible from documented<br>dependencies/confguration.    | Clean-clone test.                                       |
| NFR-029           | Recovery                     | Background jobs must tolerate<br>retry and restart without duplicate<br>business efects.<br>    | Idempotency keys/state checks.                          |
| NFR-030           | Privacy/Governance           | Data classifcation must support<br>PUBLIC, INTERNAL,<br>CONFIDENTIAL and SENSITIVE<br>handling. | Access policies.                                        |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **57. Appendix G — Business Rules and Calculation Contracts**

## **G.1 Recommendation contract**

A recommendation is valid only when the system can identify the decision state, the alternatives considered, the feasibility result, the numerical outputs, the relevant model versions and the assumptions under which the recommendation was produced.

```
Recommendation = { action, booking_window, vessel_strategy, port_strategy, berth_strategy,
route_strategy, contract_strategy, expected_cost, p95_cost, cvar, expected_saving,
laycan_probability, stockout_probability, forecast_confidence, decision_confidence, factors[],
alternatives[], constraints[], state_snapshot_id, model_versions[] }
```

## **G.2 Decision confidence**

- Forecast confidence describes predictive uncertainty; it does not guarantee a business decision is robust.

- Decision confidence should consider margin over alternatives, hard/soft constraint stability, data quality, forecast uncertainty and scenario sensitivity.

- Low data quality or weak dominance must reduce decision confidence even when a forecast model is strong.

## **G.3 Charter Now / Wait contract**

The timing engine must compare booking windows using expected and downside outcomes, not only the median freight forecast. The comparison must include future freight uncertainty, vessel availability, congestion, delay, inventory exposure and risk tolerance.

```
CostOfWaiting(window) = expected_economic_change + incremental_operational_risk +
inventory_exposure + probability_weighted_disruption_impact
```

The expression is an implementation contract, not a claim that each term must be linear. The concrete model must document how each term is calculated and avoid double counting between cost and risk engines.

## **G.4 Landed-cost contract**

The landed-cost engine is the numerical source of truth for cost. Frontend, copilot and dynamic agents must not independently recalculate business costs. Each material component must remain separately inspectable with currency, unit, source and assumption metadata.

## **G.5 Feasibility contract**

Physical infeasibility is a gating condition. A candidate that violates hard vessel, channel, berth, cargo or operational limits cannot be selected as the preferred commercial option merely because its estimated freight is lower.

## **G.6 Scenario contract**

Scenario runs must operate on a copied decision state. Baseline state must remain unchanged. Each scenario stores its seed, parameter changes, model versions, resulting metrics and recommendation delta.

## **G.7 Agent boundary contract**

Dynamic agents can retrieve, plan, compare, explain and orchestrate approved tools. They cannot create unsupported numerical values, override hard constraints, approve commercial actions or mutate authoritative state without entering the corresponding backend workflow.

## **G.8 Data-status contract**

| **Status**<br>LIVE | **Meaning**<br>Known external/operational source<br>considered current | **Allowed Behavior**<br>May support production-like decision path<br>with freshness metadata. |
| ------------------ | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| DELAYED            | Source is valid but known to lagcurrent time                           | Maybe used with visible freshness warning.                                                    |
| ESTIMATED          | Derived or estimated rather than directly<br>observed                  | Must be labeled and confdence shown.                                                          |
| SYNTHETIC          | Programmatically generated                                             | Neverpresent as live external evidence.                                                       |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

| **Status** | **Meaning**<br>test/development data              | **Allowed Behavior**                  |
| ---------- | ------------------------------------------------- | ------------------------------------- |
| DEMO       | Controlled scenario data for SIH<br>demonstration | Must be visibly labeled as demo data. |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **58. Appendix H — Release Acceptance Checklist**

## **Product**

- ☐ Core product promise is demonstrable: NAVISAIL determines when to book, vessel/port/route/contract strategy, risk-adjusted landed cost and why.

- ☐ Core loop works end-to-end: Predict → Simulate → Optimize → Decide.

- ☐ No critical feature depends on unsupported LLM-generated numbers.

## **Data**

- ☐ All material data has source, timestamp, quality, freshness and status.

- ☐ DEMO/SYNTHETIC labels are visible in APIs and UI.

- ☐ Data degradation paths are documented.

## **Numerical**

- ☐ Forecasts are backtested and leakage controls are verified.

- ☐ Compatibility excludes infeasible candidates.

- ☐ Landed cost is decomposed and traceable.

- ☐ Optimizer returns feasible alternatives or explicit infeasibility.

- ☐ Charter Now/Wait is reproducible.

- ☐ Monte Carlo outputs are deterministic in demo mode.

- ☐ Inventory can change the decision when material.

## **AI**

- ☐ Copilot uses approved tools.

- ☐ Dynamic agents are bounded by budget and permissions.

- ☐ AI cannot approve or execute commercial decisions.

## **Frontend**

- ☐ Primary screens share one decision session.

- ☐ Loading/error/empty states are handled.

- ☐ Accessibility checks pass.

- ☐ 3D is optional and performance-safe.

## **Security/Governance**

- ☐ RBAC is server-enforced.

- ☐ Approval actions are audited.

- ☐ Audit records are immutable.

- ☐ Secrets are externalized.

## **Operations**

- ☐ Health endpoints pass.

- ☐ Workers and realtime events are observable.

- ☐ Fresh environment deployment succeeds.

- ☐ Rollback/recovery documentation exists.

## **SIH Demo**

- ☐ Canonical 150,000 MT Australia-to-Bokaro scenario works from reset.

- ☐ Paradip outage/congestion shock propagates to recommendation.

- ☐ Contract and Monte Carlo comparison are visible.

- ☐ Copilot explains the final decision using grounded outputs.

- ☐ Audit trail can be shown to judges.

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline

# **59. Appendix I — Glossary and Controlled Terminology**

| **Term**                            | **Controlled Defnition**<br>                                                                                   |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| AIS                                 | Automatic Identifcation System; maritime position/identity signal<br>used for vessel intelligence.<br>         |
| Berth                               | Specifc terminal/port handling location subject to technical and<br>operational constraints.                   |
| Capesize/Panamax/Supramax/Handysize | Bulk-vessel classes used for segmentation and decision analysis.                                               |
| Charter Now / Wait                  | Decision feature comparing immediate booking against future<br>bookingwindows.                                 |
| Cost of Waiting                     | Economic and operational value/cost associated with delaying a<br>charter decision.<br>                        |
| COA                                 | Contract of Afreightment strategy for committed cargo volume over<br>voyages/time.                             |
| CVaR                                | Conditional Value at Risk; tail-loss measure for adverse outcomes<br>beyond apercentile threshold.             |
| Decision Session                    | Persistent shared context for one shipment and its analysis,<br>recommendations,scenarios and approvals.       |
| Digital Twin                        | Stateful simulation representation of maritime/logistics entities and<br>their interactions.                   |
| ETA                                 | Estimated Time of Arrival.<br>                                                                                 |
| Laycan                              | Laydays/cancelling window defning acceptable timing for a voyage or<br>charter.                                |
| Landed Cost                         | Total relevant logistics/landed economic cost rather than ocean<br>freight alone.                              |
| MaritimeStateVector                 | Canonical versioned state snapshot consumed by downstream<br>NAVISAIL engines.                                 |
| Monte Carlo                         | Repeated probabilistic scenario simulation to estimate outcome<br>distributions.                               |
| P95                                 | 95th percentile outcome; used to represent adverse-but-plausible<br>cost/risk level.                           |
| Risk-adjusted Cost                  | Cost measure incorporating explicit downside/risk considerations<br>rather than onlyexpected value.            |
| Spot Charter                        | Voyage-level spotprocurement strategy.                                                                         |
| Time Charter                        | Strategybased on charteringvessel capacityover a timeperiod.                                                   |
| What-if Scenario                    | Copied decision state with altered assumptions used to evaluate<br>alternative outcomes.                       |
| Decision Confdence                  | Confdence that the selected option remains robust relative to<br>alternatives,constraints and uncertainty.<br> |
| Forecast Confdence                  | Confdence/quality indicator associated with a predictive forecast<br>and its uncertainty.                      |

NAVISAIL AI — Product Requirements Document v1.1 — Greenfield Implementation Baseline
