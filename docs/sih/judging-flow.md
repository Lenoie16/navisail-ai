# SIH Judging Flow

Run the journey from the repository root:

```bash
PYTHONPATH=backend .venv/bin/python scripts/run_demo.py
```

Use the labeled output and the frontend routes together. The sequence is
designed to tell one coherent story: a procurement manager must choose a
defensible movement plan while keeping plant supply and downside risk visible.

| Step | Screen / action | Innovation to explain | Evidence / expected observation |
| --- | --- | --- | --- |
| 1 | Open Command Center and select the canonical session. | One decision session, not disconnected tools. | `au-steel-east-india`, 150,000 MT Australia → Bokaro; source status is visible. |
| 2 | Review Maritime State and Port Twin. | State vector and spatial twin connect vessel, route, port, berth, and plant context. | Paradip and Dhamra context; 2D fallback remains available. |
| 3 | Open Freight Intelligence. | Forecasts include uncertainty and provenance. | Demonstrate that unavailable authoritative inputs remain unavailable rather than fabricated. |
| 4 | Review vessel candidates and compatibility. | Hard constraints prevent an infeasible vessel from being selected. | Candidate and berth compatibility results show explicit reasons. |
| 5 | Compare cost and timing. | Landed cost includes delay, FX, disruption, risk, and inventory effects. | Explain the calculation contract and Charter Now / Wait output. |
| 6 | Compare contract strategies. | Spot, COA, time-charter, and hybrid strategies are evaluated in one frame. | Contracts screen shows structured comparison over supplied alternatives. |
| 7 | Run the baseline risk view. | Monte Carlo is reproducible and baseline is immutable. | Fixed seed `26006`; baseline reference is preserved. |
| 8 | Apply `congestion_plus_5_days` to Paradip. | What-if analysis changes the scenario without mutating the decision session. | Scenario output, deltas, and recommendation impact are explicit. |
| 9 | Ask Copilot “Why was Paradip preferred?” | Conversational access is constrained by approved tools and evidence. | Tool activity and source references are shown; no invented numerical values. |
| 10 | Review Recommendation. | Optimization becomes an explainable action, not an opaque score. | Recommendation, alternatives, assumptions, risks, and evidence are readable. |
| 11 | Open Execution and approve only when authorized. | Human-in-the-loop governance prevents automatic commercial action. | Demo approval/execution is labeled side-effect-free. |
| 12 | Open Audit. | Every important transition is inspectable after the decision. | Readable decision, model, approval, and execution history. |

## Judge prompts

- “Which values are authoritative, estimated, delayed, synthetic, or
  unavailable?”
- “What changes when congestion increases by five days?”
- “How do you know an infeasible vessel was not selected?”
- “Where is the approval boundary, and what is audited?”
- “What would need to be connected before this is production operations?”
