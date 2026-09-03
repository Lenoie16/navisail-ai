import { describe, expect, it } from "vitest";
import { StatusBadge } from "../components/ui";
import {
  decisionSessions,
  initialPlannerProgress,
  validatePlannerDraft,
} from "../state/decision-session";
import { forecastHorizonOptions } from "../lib/api";
import { rankAlternatives } from "../lib/recommendations";
import { CompatibilitySummary } from "../components/ports";
import { validateStrategyRequest } from "../lib/contracts";
import {
  cloneAlternative,
  defaultScenarioControls,
  scenarioControlsToRiskScenario,
} from "../state/scenarios";
import { eventActivity, suggestedQuestions } from "../state/copilot";
import { executionStatusLabels, readableAuditDetails } from "../state/workflow";
import { realtimeReducer, initialRealtimeState } from "../state/realtime";

describe("frontend foundation", () => {
  it("has a deterministic test runner", () => {
    expect(true).toBe(true);
  });

  it("keeps demo and live data visibly distinct", () => {
    const live = StatusBadge({ status: "LIVE" });
    const demo = StatusBadge({ status: "DEMO" });

    expect(live.props.className).toContain("status-badge--live");
    expect(demo.props.className).toContain("status-badge--demo");
    expect(live.props.className).not.toBe(demo.props.className);
    expect(demo.props["aria-label"]).toBe("Data status: DEMO");
  });

  it("provides stable decision-session context for navigation", () => {
    expect(decisionSessions.map((session) => session.id)).toEqual(["default", "demo"]);
  });

  it("supports every required forecast horizon", () => {
    expect(forecastHorizonOptions).toEqual([7, 15, 30, 90]);
  });

  it("rejects invalid planner quantity and laycan", () => {
    const error = validatePlannerDraft({
      commodity: "Ore",
      quantity: "0",
      origin: "Origin",
      destination: "Plant",
      requiredArrival: "2026-10-10",
      laycanStart: "2026-10-05",
      laycanEnd: "2026-10-06",
      riskTolerance: "balanced",
      priority: "normal",
      constraints: "",
    });
    expect(error).toBe("Quantity must be greater than zero.");
  });

  it("does not mark analysis complete when backend stages are unavailable", () => {
    expect(initialPlannerProgress.analysis).toBe("pending");
  });

  it("ranks alternatives by risk-adjusted cost", () => {
    const ranked = rankAlternatives([
      { id: "B", risk_adjusted_cost: 20 },
      { id: "A", risk_adjusted_cost: 10 },
    ]);
    expect(ranked.map((alternative) => alternative.id)).toEqual(["A", "B"]);
  });

  it("keeps compatibility unevaluated when authoritative inputs are incomplete", () => {
    const result = CompatibilitySummary({ feasible: null, hardFailures: [], warnings: [] });
    expect(result.props.children).toContain("Compatibility not evaluated");
  });

  it("surfaces hard compatibility failures instead of softening them", () => {
    const result = CompatibilitySummary({
      feasible: false,
      hardFailures: ["Draft exceeds berth limit"],
      warnings: [],
    });
    expect(result.props.className).toContain("compatibility-result--failed");
    expect(result.props.children[1].props.children).toContain("Hard failures exclude");
  });

  it("rejects unordered strategy quantiles before sending a request", () => {
    expect(
      validateStrategyRequest({
        voyages: [
          {
            voyage_id: "v1",
            volume_tonnes: 1,
            spot_p10: 5,
            spot_p50: 3,
            spot_p90: 6,
            coa_rate: 4,
            time_charter_rate: 5,
          },
        ],
        market_condition: "stable",
      }),
    ).toBe("Spot quantiles must be ordered.");
  });

  it("maps what-if controls to backend risk fields without approximating inventory", () => {
    const scenario = scenarioControlsToRiskScenario({
      ...defaultScenarioControls,
      freightSpike: 0.5,
      congestion: 0.25,
      cyclone: 0.5,
      delay: 0.5,
    });

    expect(scenario.name).toBe("what-if");
    expect(scenario.freight_volatility).toBe(0.25);
    expect(scenario.congestion_probability).toBe(0.35);
    expect(scenario.weather_probability).toBe(0.6);
    expect(scenario.operational_delay_hours).toBe(2.5);
    expect("inventory_shock" in scenario).toBe(false);
  });

  it("clones alternatives so baseline inputs remain immutable", () => {
    const baseline = {
      alternative_id: "route-a",
      base_cost: 10,
      base_delay_hours: 2,
      inventory_breach_threshold_hours: 24,
      cost_threshold: 20,
      freight_exposure: 1,
      fuel_exposure: 0,
      fx_exposure: 0,
    };
    const scenario = cloneAlternative(baseline);
    scenario.base_cost = 99;

    expect(baseline.base_cost).toBe(10);
    expect(scenario.base_cost).toBe(99);
  });

  it("maps copilot tool events to transparent activities", () => {
    expect(
      eventActivity({
        type: "tool_started",
        agent_id: "agent-1",
        session_id: "default",
        message: "Running Monte Carlo",
        tool: "run_monte_carlo",
        metadata: {},
      }),
    ).toBe("simulating");
    expect(suggestedQuestions).toContain("Should we charter now?");
  });

  it("keeps workflow statuses readable and audit details structured", () => {
    expect(executionStatusLabels.booking_in_progress).toBe("Booking in progress");
    expect(readableAuditDetails({ role: "approver", status: "approved" })).toEqual([
      "role: approver",
      "status: approved",
    ]);
  });

  it("deduplicates realtime events while retaining the latest event timestamp", () => {
    const event = {
      event_id: "evt-1",
      event_type: "recommendation.updated" as const,
      occurred_at: "2026-09-03T10:00:00Z",
      correlation_id: "corr-1",
      sequence: 1,
      payload: {},
    };
    const next = realtimeReducer(initialRealtimeState, { type: "event", event });
    const duplicate = realtimeReducer(next, { type: "event", event });
    expect(next.events).toHaveLength(1);
    expect(duplicate).toBe(next);
    expect(next.lastUpdatedAt).toBe(event.occurred_at);
  });
});
