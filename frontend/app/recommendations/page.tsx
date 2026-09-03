"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import {
  Button,
  EmptyState,
  ErrorState,
  MetricCard,
  RecommendationCard,
  StatusBadge,
} from "../../components/ui";
import { createApproval } from "../../lib/api";

export default function RecommendationsPage() {
  const [actionState, setActionState] = useState("No recommendation loaded");
  const [error, setError] = useState<string | null>(null);

  async function requestApproval() {
    setError(null);
    setActionState("Requesting approval…");
    try {
      const approval = await createApproval(
        "selected-recommendation",
        "unavailable",
        "current-user",
        "approver",
      );
      setActionState(`Approval ${approval.status}`);
    } catch (reason: unknown) {
      setActionState("Approval not submitted");
      setError(reason instanceof Error ? reason.message : "Approval request failed.");
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Decision workspace</p>
            <h1>Recommendation</h1>
            <p>
              Review the preferred path, alternatives, and decision evidence before taking action.
            </p>
          </div>
          <StatusBadge status="ESTIMATED" />
        </header>

        <RecommendationCard title="Preferred decision">
          <EmptyState title="Select a recommendation" />
          <div className="recommendation-actions">
            <Button variant="quiet" disabled>
              Review
            </Button>
            <Button onClick={requestApproval} disabled={actionState === "Requesting approval…"}>
              Approve
            </Button>
            <Button variant="quiet" disabled>
              Reject
            </Button>
            <Button variant="quiet" disabled>
              Send back
            </Button>
            <Button variant="quiet" disabled>
              Simulate alternative
            </Button>
          </div>
          <p className="chart-note" aria-live="polite">
            {actionState}
          </p>
          {error && <ErrorState message={error} />}
        </RecommendationCard>

        <section className="metric-grid" aria-label="Recommendation metrics">
          <MetricCard
            label="Expected landed cost"
            value="—"
            hint="Backend recommendation required"
          />
          <MetricCard label="Risk-adjusted cost" value="—" hint="Not calculated in UI" />
          <MetricCard label="Arrival expectation" value="—" hint="Awaiting recommendation" />
          <MetricCard label="Decision confidence" value="—" hint="Evidence not loaded" />
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Charter now / wait</h2>
            <p className="lede">
              Timing guidance is indeterminate until a recommendation includes timing economics.
            </p>
            <StatusBadge status="ESTIMATED" />
          </section>
          <section className="glass-panel">
            <h2>Logistics path</h2>
            <ul className="data-list">
              <li>
                <strong>Vessel / port / berth</strong>
                <span>—</span>
              </li>
              <li>
                <strong>Route / contract</strong>
                <span>—</span>
              </li>
              <li>
                <strong>Delay / inventory impact</strong>
                <span>—</span>
              </li>
            </ul>
          </section>
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Ranked alternatives</h2>
            <EmptyState title="No alternatives loaded" />
          </section>
          <section className="glass-panel">
            <h2>Why this recommendation?</h2>
            <ul className="data-list">
              <li>
                <strong>Rationale</strong>
                <span>Awaiting explanation</span>
              </li>
              <li>
                <strong>What could go wrong?</strong>
                <span>Awaiting risk scenarios</span>
              </li>
              <li>
                <strong>Why not option B?</strong>
                <span>Awaiting counterfactual</span>
              </li>
              <li>
                <strong>Assumptions</strong>
                <span>Awaiting source data</span>
              </li>
            </ul>
          </section>
        </section>
      </main>
    </Shell>
  );
}
