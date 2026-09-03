export type DecisionSessionState = { id?: string };

export type PlannerStep = "shipment" | "session" | "maritime-state" | "analysis";
export type PlannerStepStatus = "pending" | "running" | "complete" | "unavailable" | "failed";

export type PlannerProgress = Record<PlannerStep, PlannerStepStatus>;

export const initialPlannerProgress: PlannerProgress = {
  shipment: "pending",
  session: "pending",
  "maritime-state": "pending",
  analysis: "pending",
};

export type PlannerDraft = {
  commodity: string;
  quantity: string;
  origin: string;
  destination: string;
  requiredArrival: string;
  laycanStart: string;
  laycanEnd: string;
  riskTolerance: string;
  priority: string;
  constraints: string;
};

export function validatePlannerDraft(draft: PlannerDraft): string | null {
  if (!draft.commodity.trim() || !draft.origin.trim() || !draft.destination.trim()) {
    return "Commodity, origin, and destination plant are required.";
  }
  const quantity = Number(draft.quantity);
  if (!Number.isFinite(quantity) || quantity <= 0) return "Quantity must be greater than zero.";
  if (!draft.requiredArrival) return "Required arrival date is required.";
  if (draft.laycanStart && draft.laycanEnd && draft.laycanStart > draft.laycanEnd) {
    return "Laycan start must be on or before laycan end.";
  }
  if (draft.laycanEnd && draft.requiredArrival && draft.laycanEnd > draft.requiredArrival) {
    return "Laycan must finish on or before the required arrival date.";
  }
  return null;
}

export const decisionSessions = [
  { id: "default", label: "Current decision session" },
  { id: "demo", label: "Demo scenario" },
] as const;
