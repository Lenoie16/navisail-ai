"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import { Button, EmptyState, ErrorState, LoadingState, StatusBadge } from "../../components/ui";
import { fetchAudit, type AuditEvent } from "../../lib/api";
import { formatAuditEvent, readableAuditDetails } from "../../state/workflow";

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function loadAudit() {
    setLoading(true);
    setError(null);
    try {
      setEvents(await fetchAudit("recommendation", "selected-recommendation"));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Audit history could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Traceability</p>
            <h1>Audit</h1>
            <p>Inspect decision provenance, workflow history, and operational transitions.</p>
          </div>
          <StatusBadge status="LIVE" />
        </header>
        <section className="glass-panel">
          <div className="recommendation-actions">
            <Button onClick={() => void loadAudit()} disabled={loading}>
              {loading ? "Loading audit…" : "Load audit history"}
            </Button>
          </div>
          {error && <ErrorState message={error} />}
          {loading ? (
            <LoadingState />
          ) : events.length === 0 && !error ? (
            <EmptyState title="No audit records loaded" />
          ) : (
            <div className="audit-timeline">
              {events.map((event) => (
                <article className="audit-event" key={event.event_id}>
                  <strong>{event.action}</strong>
                  <p>{formatAuditEvent(event)}</p>
                  <dl className="audit-details">
                    {readableAuditDetails(event.details).map((detail) => {
                      const [label, ...value] = detail.split(": ");
                      return (
                        <div key={detail}>
                          <dt>{label}</dt>
                          <dd>{value.join(": ")}</dd>
                        </div>
                      );
                    })}
                  </dl>
                </article>
              ))}
            </div>
          )}
        </section>
        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Decision and model provenance</h2>
            <ul className="data-list">
              <li>
                <strong>Decision state</strong>
                <span>Unavailable until record is selected</span>
              </li>
              <li>
                <strong>Source timestamps</strong>
                <span>Unavailable until record is selected</span>
              </li>
              <li>
                <strong>Model versions</strong>
                <span>Unavailable until recommendation is loaded</span>
              </li>
              <li>
                <strong>Constraints</strong>
                <span>Unavailable until recommendation is loaded</span>
              </li>
            </ul>
          </section>
          <section className="glass-panel">
            <h2>Approval and execution history</h2>
            <ul className="data-list">
              <li>
                <strong>Recommendation changes</strong>
                <span>Shown from audit events when available</span>
              </li>
              <li>
                <strong>Approval history</strong>
                <span>Shown from audit events when available</span>
              </li>
              <li>
                <strong>Execution events</strong>
                <span>Shown from audit events when available</span>
              </li>
            </ul>
          </section>
        </section>
      </main>
    </Shell>
  );
}
