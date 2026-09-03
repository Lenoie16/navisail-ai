"use client";

import { useEffect, useMemo, useState } from "react";
import { Shell } from "../../components/layout";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  MetricCard,
  RecommendationCard,
  Select,
  StatusBadge,
  Timeline,
} from "../../components/ui";
import { decisionSessions } from "../../state/decision-session";
import { fetchResource, type ApiResource } from "../../lib/api";

type DashboardState = {
  shipments: ApiResource[];
  vessels: ApiResource[];
  ports: ApiResource[];
};

export default function CommandCenterPage() {
  const [sessionId, setSessionId] = useState("default");
  const [data, setData] = useState<DashboardState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError(null);
    Promise.all([
      fetchResource("shipments", controller.signal),
      fetchResource("vessels", controller.signal),
      fetchResource("ports", controller.signal),
    ])
      .then(([shipments, vessels, ports]) => setData({ shipments, vessels, ports }))
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError") return;
        setError(reason instanceof Error ? reason.message : "Unable to load command center data.");
      });
    return () => controller.abort();
  }, [refreshKey]);

  const activeSession = useMemo(
    () => decisionSessions.find((session) => session.id === sessionId) ?? decisionSessions[0],
    [sessionId],
  );

  return (
    <Shell sessionId={activeSession.id}>
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Operational overview</p>
            <h1>Command center</h1>
            <p>Decision-ready maritime context, with provenance visible at every layer.</p>
          </div>
          <StatusBadge status={data ? "ESTIMATED" : "DEMO"} />
        </header>

        <section className="glass-panel session-bar" aria-label="Decision session">
          <label htmlFor="decision-session">Decision session</label>
          <Select
            id="decision-session"
            value={activeSession.id}
            onChange={(event) => setSessionId(event.target.value)}
          >
            {decisionSessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.label}
              </option>
            ))}
          </Select>
          <button
            type="button"
            className="primary"
            onClick={() => setRefreshKey((value) => value + 1)}
          >
            Refresh signals
          </button>
        </section>

        {error ? <ErrorState message={error} /> : !data ? <LoadingState /> : null}

        <section className="metric-grid" aria-label="Command metrics">
          <MetricCard
            label="Open shipments"
            value={data ? data.shipments.length : "—"}
            hint="Backend resource count"
          />
          <MetricCard label="Active voyages" value="—" hint="No voyage feed connected" />
          <MetricCard
            label="High-risk decisions"
            value="—"
            hint="Recommendation analysis required"
          />
          <MetricCard
            label="State freshness"
            value={data ? "ESTIMATED" : "DEMO"}
            hint="Source status is explicit"
          />
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Maritime context</h2>
            {data ? (
              <ul className="data-list">
                <li>
                  <strong>Vessel availability</strong>
                  <span>{data.vessels.length} records</span>
                </li>
                <li>
                  <strong>Port network</strong>
                  <span>{data.ports.length} records</span>
                </li>
                <li>
                  <strong>Route map</strong>
                  <span>Awaiting geospatial feed</span>
                </li>
              </ul>
            ) : (
              <LoadingState />
            )}
          </section>
          <section className="glass-panel">
            <h2>Market and freight outlook</h2>
            <p className="lede">
              Forecast and congestion signals will appear here when a decision session provides
              inputs.
            </p>
            <StatusBadge status="ESTIMATED" />
          </section>
        </section>

        <section className="panel-grid">
          <RecommendationCard title="Priority recommendation">
            <EmptyState title="No recommendation selected" />
          </RecommendationCard>
          <section className="glass-panel">
            <h2>Risk and plant exposure</h2>
            <ul className="data-list">
              <li>
                <strong>Congestion exposure</strong>
                <span>—</span>
              </li>
              <li>
                <strong>Stockout exposure</strong>
                <span>—</span>
              </li>
              <li>
                <strong>Risk alerts</strong>
                <span>—</span>
              </li>
            </ul>
          </section>
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Active scenarios</h2>
            <EmptyState title="No active scenarios" />
          </section>
          <section className="glass-panel">
            <h2>Event timeline</h2>
            <Timeline items={["State snapshot", "Feasibility", "Cost model", "Recommendation"]} />
          </section>
        </section>
      </main>
    </Shell>
  );
}
