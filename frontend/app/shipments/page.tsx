"use client";

import { useState, type FormEvent } from "react";
import { Shell } from "../../components/layout";
import { Button, ErrorState, Input, Select } from "../../components/ui";
import { createShipment } from "../../lib/api";
import {
  initialPlannerProgress,
  validatePlannerDraft,
  type PlannerDraft,
  type PlannerProgress,
} from "../../state/decision-session";

const initialDraft: PlannerDraft = {
  commodity: "",
  quantity: "",
  origin: "",
  destination: "",
  requiredArrival: "",
  laycanStart: "",
  laycanEnd: "",
  riskTolerance: "balanced",
  priority: "normal",
  constraints: "",
};

const progressLabels: Record<keyof PlannerProgress, string> = {
  shipment: "Create shipment",
  session: "Create decision session",
  "maritime-state": "Load maritime state",
  analysis: "Begin analysis",
};

export default function ShipmentsPage() {
  const [draft, setDraft] = useState(initialDraft);
  const [progress, setProgress] = useState<PlannerProgress>(initialPlannerProgress);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  function update(field: keyof PlannerDraft, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validatePlannerDraft(draft);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError(null);
    setSubmitted(true);
    setProgress((current) => ({ ...current, shipment: "running" }));
    try {
      await createShipment({
        reference: `${draft.commodity.trim()}-${Date.now()}`,
        quantity_tonnes: Number(draft.quantity),
        planned_arrival_at: new Date(`${draft.requiredArrival}T00:00:00Z`).toISOString(),
      });
      setProgress({
        shipment: "complete",
        session: "unavailable",
        "maritime-state": "unavailable",
        analysis: "unavailable",
      });
    } catch (reason: unknown) {
      setProgress((current) => ({ ...current, shipment: "failed" }));
      setError(reason instanceof Error ? reason.message : "Shipment creation failed.");
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Planning workspace</p>
            <h1>Create shipment</h1>
            <p>Define cargo requirements before evaluating vessels, ports, timing, and risk.</p>
          </div>
          <span className="status-badge status-badge--demo">DEMO</span>
        </header>

        <div className="planner-layout">
          <form className="glass-panel planner-form" onSubmit={submit} noValidate>
            <h2>Shipment requirements</h2>
            <label>
              Commodity
              <Input
                required
                value={draft.commodity}
                onChange={(e) => update("commodity", e.target.value)}
              />
            </label>
            <label>
              Quantity (tonnes)
              <Input
                required
                min="0.01"
                step="0.01"
                type="number"
                value={draft.quantity}
                onChange={(e) => update("quantity", e.target.value)}
              />
            </label>
            <label>
              Origin
              <Input
                required
                value={draft.origin}
                onChange={(e) => update("origin", e.target.value)}
              />
            </label>
            <label>
              Destination plant
              <Input
                required
                value={draft.destination}
                onChange={(e) => update("destination", e.target.value)}
              />
            </label>
            <label>
              Required arrival
              <Input
                required
                type="date"
                value={draft.requiredArrival}
                onChange={(e) => update("requiredArrival", e.target.value)}
              />
            </label>
            <div className="field-grid">
              <label>
                Laycan start
                <Input
                  type="date"
                  value={draft.laycanStart}
                  onChange={(e) => update("laycanStart", e.target.value)}
                />
              </label>
              <label>
                Laycan end
                <Input
                  type="date"
                  value={draft.laycanEnd}
                  onChange={(e) => update("laycanEnd", e.target.value)}
                />
              </label>
            </div>
            <div className="field-grid">
              <label>
                Risk tolerance
                <Select
                  value={draft.riskTolerance}
                  onChange={(e) => update("riskTolerance", e.target.value)}
                >
                  <option>conservative</option>
                  <option>balanced</option>
                  <option>aggressive</option>
                </Select>
              </label>
              <label>
                Priority
                <Select value={draft.priority} onChange={(e) => update("priority", e.target.value)}>
                  <option>normal</option>
                  <option>high</option>
                  <option>urgent</option>
                </Select>
              </label>
            </div>
            <label>
              Optional constraints
              <textarea
                value={draft.constraints}
                onChange={(e) => update("constraints", e.target.value)}
              />
            </label>
            {error && <ErrorState message={error} />}
            <Button type="submit" disabled={submitted && progress.shipment === "running"}>
              Create shipment and begin analysis
            </Button>
          </form>

          <section className="glass-panel planner-progress" aria-live="polite">
            <h2>Analysis progress</h2>
            <p className="lede">
              The workflow reports each backend stage explicitly. It will not claim analysis is
              complete while a job is pending or unavailable.
            </p>
            <ol className="data-list">
              {(Object.keys(progressLabels) as Array<keyof PlannerProgress>).map((step) => (
                <li key={step}>
                  <strong>{progressLabels[step]}</strong>
                  <span>{progress[step]}</span>
                </li>
              ))}
            </ol>
            {progress.analysis === "unavailable" && (
              <p className="chart-note">
                Decision-session and analysis-job endpoints are not available yet.
              </p>
            )}
          </section>
        </div>
      </main>
    </Shell>
  );
}
