export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
export const forecastHorizonOptions = [7, 15, 30, 90] as const;

export type ApiResource = { id?: string; name?: string; status?: string };

export type PortResource = ApiResource & {
  unlocode?: string;
  country_code?: string;
  location?: string;
  handling_capability?: string | null;
  congestion_status?: string | null;
  operational_status?: string;
  active?: boolean;
};

export type BerthResource = ApiResource & {
  port_id?: string;
  code?: string;
  max_loa_m?: number | string | null;
  max_beam_m?: number | string | null;
  max_draft_m?: number | string | null;
  max_dwt_tonnes?: number | string | null;
  cargo_constraints?: string | null;
  operational_restrictions?: string | null;
  working_capability?: string | null;
  active?: boolean;
};

export type VesselResource = ApiResource & {
  vessel_type?: string;
  imo_number?: string;
  operator?: string | null;
  deadweight_tonnes?: number | string | null;
  loa_m?: number | string | null;
  beam_m?: number | string | null;
  max_draft_m?: number | string | null;
  speed_knots?: number | string | null;
};

export type CompatibilityResult = {
  feasible: boolean;
  hard_failures: string[];
  soft_constraints: string[];
  warnings: string[];
  limiting_factor: string | null;
  berth_id: string | null;
  berth_level_compatibility: Record<string, boolean>;
  confidence: number;
  supporting_evidence: string[];
  penalty: number;
};

export type CompatibilityCheckRequest = {
  vessel: Record<string, unknown>;
  port: Record<string, unknown>;
  cargo: Record<string, unknown>;
  berth_id?: string;
};

export type VoyageDemand = {
  voyage_id: string;
  volume_tonnes: number;
  spot_p10: number;
  spot_p50: number;
  spot_p90: number;
  coa_rate: number;
  time_charter_rate: number;
  spot_reliability?: number;
  coa_reliability?: number;
  time_charter_reliability?: number;
};

export type StrategyConstraints = {
  risk_tolerance?: number;
  inventory_pressure?: number;
  minimum_coa_share?: number;
  maximum_time_charter_share?: number;
  strategic_flexibility_floor?: number;
};

export type StrategyAlternative = {
  strategy: "Spot" | "COA" | "Time Charter" | "Hybrid";
  volume_allocation: Record<string, number>;
  expected_cost: number;
  risk: number;
  schedule_reliability: number;
  downside_exposure: number;
  flexibility: number;
  objective_value: number;
  justification: string;
};

export type StrategyOptimizationResult = {
  recommended_strategy: StrategyAlternative["strategy"];
  recommended_allocation: Record<string, number>;
  expected_cost: number;
  alternatives: StrategyAlternative[];
  market_condition: "stable" | "volatile" | "rising" | "falling";
  total_volume_tonnes: number;
  explanation: string;
};

export type StrategyRequest = {
  voyages: VoyageDemand[];
  market_condition: StrategyOptimizationResult["market_condition"];
  constraints?: StrategyConstraints;
};

export type RiskScenario = {
  name: string;
  freight_volatility: number;
  fuel_volatility: number;
  congestion_probability: number;
  waiting_hours: number;
  weather_probability: number;
  vessel_failure_probability: number;
  port_outage_probability: number;
  fx_volatility: number;
  operational_delay_hours: number;
  disruption_cost: number;
};

export type SimulationAlternative = {
  alternative_id: string;
  base_cost: number;
  base_delay_hours: number;
  inventory_breach_threshold_hours: number;
  cost_threshold: number;
  freight_exposure: number;
  fuel_exposure: number;
  fx_exposure: number;
};

export type SimulationOutput = {
  alternative_id: string;
  simulations: number;
  seed: number;
  scenario: string;
  p10: number;
  p50: number;
  p90: number;
  mean: number;
  variance: number;
  cvar_90: number;
  probability_of_delay: number;
  probability_exceeding_cost_threshold: number;
  probability_inventory_breach: number;
  mean_delay_hours: number;
};

export type RiskCompareRequest = {
  alternatives: SimulationAlternative[];
  scenario: RiskScenario;
  simulations: number;
  seed: number;
};

export type RiskCompareResponse = Record<string, SimulationOutput>;

export type ShipmentCreateRequest = {
  reference: string;
  quantity_tonnes: number;
  planned_arrival_at?: string;
};

export type Shipment = ShipmentCreateRequest & { id: string };

export async function createShipment(
  request: ShipmentCreateRequest,
  signal?: AbortSignal,
): Promise<Shipment> {
  const response = await fetch(`${apiBaseUrl}/shipments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Unable to create shipment (${response.status})`);
  }

  return (await response.json()) as Shipment;
}

export type RecommendationAlternative = {
  option_id: string;
  vessel_id: string;
  port_id: string;
  berth_id: string;
  route_id: string;
  expected_landed_cost: number;
  risk_adjusted_cost: number;
  expected_arrival: string;
  delay_risk: number;
  inventory_impact: number;
  explanation: string;
};

export type Recommendation = {
  decision: "Recommended" | "No Feasible Alternative";
  preferred_strategy: string;
  preferred_vessel: string | null;
  preferred_port: string | null;
  preferred_berth: string | null;
  preferred_booking_timing: string | null;
  preferred_contract: string | null;
  expected_landed_cost: number | null;
  risk_adjusted_cost: number | null;
  expected_arrival: string | null;
  delay_risk: number | null;
  inventory_impact: number | null;
  confidence: number;
  data_confidence: number;
  model_confidence: number;
  decision_confidence: number;
  alternatives: RecommendationAlternative[];
  key_assumptions: string[];
  main_drivers: string[];
  major_downside_scenarios: string[];
  source_state_snapshot: string;
  model_versions: Record<string, string>;
  parameter_version: string;
  reproducibility_key: string;
  explanation: string;
};

export type ApprovalDecision = {
  decision_id: string;
  recommendation_id?: string;
  recommendation_version?: string;
  status: string;
  user?: string;
  role?: string;
  comment?: string;
  created_at?: string;
  decided_at?: string | null;
  expires_at?: string | null;
};

export async function createApproval(
  recommendationId: string,
  recommendationVersion: string,
  user: string,
  role: string,
): Promise<ApprovalDecision> {
  const response = await fetch(`${apiBaseUrl}/execution/approvals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      recommendation_id: recommendationId,
      recommendation_version: recommendationVersion,
      user,
      role,
    }),
  });
  if (!response.ok) throw new Error(`Approval request rejected (${response.status})`);
  return (await response.json()) as ApprovalDecision;
}

export type ApprovalDecisionRequest = {
  user: string;
  role: string;
  status: "approved" | "rejected" | "returned_for_revision";
  comment?: string;
};

export type ExecutionStatus =
  | "draft"
  | "approved"
  | "booking_requested"
  | "booking_in_progress"
  | "booked"
  | "voyage_active"
  | "completed"
  | "cancelled";

export type ExecutionRecord = {
  execution_id: string;
  recommendation_id: string;
  status: ExecutionStatus;
  updated_at: string;
  updated_by: string;
  approval_id?: string | null;
};

export type AuditEvent = {
  event_id: string;
  actor: string;
  action: string;
  entity_type: string;
  entity_id: string;
  occurred_at: string;
  details: Record<string, unknown>;
};

export async function decideApproval(
  decisionId: string,
  request: ApprovalDecisionRequest,
  signal?: AbortSignal,
): Promise<ApprovalDecision> {
  const response = await fetch(`${apiBaseUrl}/execution/approvals/${decisionId}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Approval decision rejected (${response.status})`);
  return (await response.json()) as ApprovalDecision;
}

export async function createExecution(
  recommendationId: string,
  user: string,
  signal?: AbortSignal,
): Promise<ExecutionRecord> {
  const response = await fetch(`${apiBaseUrl}/execution/executions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recommendation_id: recommendationId, user }),
    signal,
  });
  if (!response.ok) throw new Error(`Execution request rejected (${response.status})`);
  return (await response.json()) as ExecutionRecord;
}

export async function transitionExecution(
  executionId: string,
  request: {
    target: ExecutionStatus;
    user: string;
    approval_id?: string;
    approval_status?: "approved" | "rejected" | "returned_for_revision" | "pending" | "expired";
  },
  signal?: AbortSignal,
): Promise<ExecutionRecord> {
  const response = await fetch(`${apiBaseUrl}/execution/executions/${executionId}/transition`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Execution transition rejected (${response.status})`);
  return (await response.json()) as ExecutionRecord;
}

export async function fetchAudit(
  entityType: string,
  entityId: string,
  signal?: AbortSignal,
): Promise<AuditEvent[]> {
  const response = await fetch(`${apiBaseUrl}/execution/audit/${entityType}/${entityId}`, {
    signal,
  });
  if (!response.ok) throw new Error(`Unable to load audit history (${response.status})`);
  return (await response.json()) as AuditEvent[];
}

export type FreightObservation = {
  observed_at: string;
  route: string;
  vessel_class: string;
  rate: number;
  currency: string;
  unit: string;
  quality_score?: number;
  features?: Record<string, number>;
};

export type ForecastResult = {
  point_forecast: number;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  interval_width: number;
  forecast_date: string;
  horizon_days: number;
  route: string;
  vessel_class: string;
  model_version: string;
  model: string;
  input_snapshot: string;
  confidence: number;
  model_confidence: number;
  data_confidence: number;
  decision_confidence: number;
  calibration_status: "calibrated" | "insufficient_history";
  data_quality: number;
  confidence_metadata: Record<string, number | string>;
};

export type ForecastRequest = {
  observations: FreightObservation[];
  route: string;
  vessel_class: string;
  horizon_days: 7 | 15 | 30 | 90;
  model?: "naive" | "rolling_mean" | "exponential_smoothing" | "auto";
};

export async function createForecast(
  request: ForecastRequest,
  signal?: AbortSignal,
): Promise<ForecastResult> {
  const response = await fetch(`${apiBaseUrl}/forecasts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Unable to create freight forecast (${response.status})`);
  }
  return (await response.json()) as ForecastResult;
}

export async function fetchResource<T extends ApiResource>(
  resource: "shipments" | "vessels" | "ports" | "berths",
  signal?: AbortSignal,
): Promise<T[]> {
  const response = await fetch(`${apiBaseUrl}/${resource}?limit=100`, { signal });
  if (!response.ok) {
    throw new Error(`Unable to load ${resource} (${response.status})`);
  }
  return (await response.json()) as T[];
}

export async function checkCompatibility(
  request: CompatibilityCheckRequest,
  signal?: AbortSignal,
): Promise<CompatibilityResult> {
  const response = await fetch(`${apiBaseUrl}/compatibility/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Unable to check compatibility (${response.status})`);
  return (await response.json()) as CompatibilityResult;
}

export async function optimizeStrategy(
  request: StrategyRequest,
  signal?: AbortSignal,
): Promise<StrategyOptimizationResult> {
  const response = await fetch(`${apiBaseUrl}/optimization/strategy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Unable to optimize contract strategy (${response.status})`);
  return (await response.json()) as StrategyOptimizationResult;
}

export async function compareRisk(
  request: RiskCompareRequest,
  signal?: AbortSignal,
): Promise<RiskCompareResponse> {
  const response = await fetch(`${apiBaseUrl}/risk/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Unable to compare risk scenarios (${response.status})`);
  return (await response.json()) as RiskCompareResponse;
}

export type CopilotAgentRequest = {
  session_id: string;
  question: string;
  source_state_snapshot: string;
  context?: Record<string, unknown>;
};

export type CopilotAgentEvent = {
  type: string;
  agent_id: string;
  session_id: string;
  message: string;
  tool?: string | null;
  metadata: Record<string, unknown>;
};

export type CopilotAgentResult = {
  status: string;
  agent_id: string;
  session_id: string;
  answer: string;
  tool_results: Record<string, unknown>;
  missing_capabilities: string[];
  events: CopilotAgentEvent[];
  reflection_loops: number;
  tool_calls: number;
  source_state_snapshot: string;
};

export async function runCopilotAgent(
  request: CopilotAgentRequest,
  signal?: AbortSignal,
): Promise<CopilotAgentResult> {
  const response = await fetch(`${apiBaseUrl}/copilot/agent/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok) throw new Error(`Unable to run NAVISAIL copilot (${response.status})`);
  return (await response.json()) as CopilotAgentResult;
}
