"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import { Button, EmptyState, ErrorState, MetricCard, StatusBadge } from "../../components/ui";
import {
  createExecution,
  decideApproval,
  type ApprovalDecision,
  type ExecutionRecord,
  transitionExecution,
} from "../../lib/api";
import { executionStatusLabels } from "../../state/workflow";
import { canAccess, type NavisailRole } from "../../lib/permissions";

const user = "current-user";
const role: NavisailRole = "approver";

export default function ExecutionPage() {
  const [approval, setApproval] = useState<ApprovalDecision | null>(null);
  const [execution, setExecution] = useState<ExecutionRecord | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function decide(status: "approved" | "rejected" | "returned_for_revision") {
    if (!approval?.decision_id) return;
    setBusy(true);
    setError(null);
    try {
      setApproval(await decideApproval(approval.decision_id, { user, role, status }));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Approval action failed.");
    } finally {
      setBusy(false);
    }
  }

  async function startExecution() {
    setBusy(true);
    setError(null);
    try {
      setExecution(await createExecution("selected-recommendation", user));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Execution was not created.");
    } finally {
      setBusy(false);
    }
  }

  async function requestBooking() {
    if (!execution || !approval || approval.status !== "approved") return;
    setBusy(true);
    setError(null);
    try {
      setExecution(
        await transitionExecution(execution.execution_id, {
          target: "approved",
          user,
          approval_id: approval.decision_id,
          approval_status: "approved",
        }),
      );
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Execution transition failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Operational handoff</p>
            <h1>Execution</h1>
            <p>Move an approved recommendation through a controlled, auditable workflow.</p>
          </div>
          <StatusBadge status={execution ? "LIVE" : "ESTIMATED"} />
        </header>

        {error && <ErrorState message={error} />}
        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Approval review</h2>
            <p className="chart-note">Recommendation snapshot: selected recommendation</p>
            <ul className="data-list">
              <li>
                <strong>Expected landed cost</strong>
                <span>Unavailable until recommendation is loaded</span>
              </li>
              <li>
                <strong>Risk / assumptions</strong>
                <span>Unavailable until recommendation is loaded</span>
              </li>
              <li>
                <strong>User role</strong>
                <span>{role}</span>
              </li>
              <li>
                <strong>Approval status</strong>
                <span>{approval?.status ?? "No approval record"}</span>
              </li>
            </ul>
            <div className="recommendation-actions">
              {canAccess(role, "approve recommendation") && (
                <Button onClick={() => void decide("approved")} disabled={!approval || busy}>
                  Approve
                </Button>
              )}
              {canAccess(role, "approve recommendation") && (
                <>
                  <Button
                    variant="quiet"
                    onClick={() => void decide("returned_for_revision")}
                    disabled={!approval || busy}
                  >
                    Return
                  </Button>
                  <Button
                    variant="quiet"
                    onClick={() => void decide("rejected")}
                    disabled={!approval || busy}
                  >
                    Reject
                  </Button>
                </>
              )}
            </div>
            {!approval && (
              <p className="chart-note">
                Approval controls activate when an authoritative approval record is loaded.
              </p>
            )}
          </section>
          <section className="glass-panel">
            <h2>Execution state</h2>
            {!execution ? (
              <>
                <EmptyState title="No execution record loaded" />
                <Button onClick={() => void startExecution()} disabled={busy}>
                  Create execution record
                </Button>
              </>
            ) : (
              <>
                <MetricCard
                  label="Execution"
                  value={executionStatusLabels[execution.status]}
                  hint={execution.execution_id}
                />
                {canAccess(role, "execute booking") && (
                  <Button
                    onClick={() => void requestBooking()}
                    disabled={busy || approval?.status !== "approved"}
                  >
                    Request approved handoff
                  </Button>
                )}
              </>
            )}
          </section>
        </section>

        <section className="metric-grid" aria-label="Operational progress">
          <MetricCard
            label="Booking status"
            value={execution ? executionStatusLabels[execution.status] : "—"}
          />
          <MetricCard
            label="Voyage progress"
            value="Unavailable"
            hint="No voyage telemetry loaded"
          />
          <MetricCard label="ETA" value="Unavailable" hint="No operational ETA loaded" />
          <MetricCard
            label="Delays / events"
            value="Unavailable"
            hint="No execution events loaded"
          />
        </section>
      </main>
    </Shell>
  );
}
