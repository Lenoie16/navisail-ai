import type { CopilotAgentEvent } from "../lib/api";

export type CopilotActivity = "retrieving" | "calculating" | "simulating" | "comparing";

export type CopilotMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  events?: CopilotAgentEvent[];
  sources?: string[];
  missingCapabilities?: string[];
};

const activityByTool: Record<string, CopilotActivity> = {
  get_shipment: "retrieving",
  get_maritime_state: "retrieving",
  get_freight_forecast: "calculating",
  get_vessel_candidates: "retrieving",
  check_port_compatibility: "calculating",
  get_congestion: "retrieving",
  calculate_landed_cost: "calculating",
  compare_booking_dates: "comparing",
  compare_contract_strategies: "comparing",
  run_monte_carlo: "simulating",
  get_inventory_risk: "calculating",
  get_recommendation: "comparing",
  get_decision_explanation: "retrieving",
};

export const suggestedQuestions = [
  "Should we charter now?",
  "Why was Paradip preferred?",
  "What happens if congestion increases by five days?",
  "Compare spot and hybrid strategy.",
  "Which vessel is feasible?",
] as const;

export function eventActivity(event: CopilotAgentEvent): CopilotActivity | null {
  return event.tool ? (activityByTool[event.tool] ?? null) : null;
}

export function sourceReferences(result: {
  source_state_snapshot: string;
  tool_results: Record<string, unknown>;
}): string[] {
  const sources = Object.entries(result.tool_results)
    .filter(([, value]) => value !== null && value !== undefined)
    .map(([key]) => `navisail.engine.${key}`);
  return [`State snapshot: ${result.source_state_snapshot}`, ...sources];
}
