"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import { ChartContainer, EmptyState, MetricCard, Select, StatusBadge } from "../../components/ui";
import { forecastHorizonOptions } from "../../lib/api";

const scenarios = ["Base market", "Rising freight", "Disrupted supply"] as const;

export default function FreightIntelligencePage() {
  const [horizon, setHorizon] = useState<(typeof forecastHorizonOptions)[number]>(30);
  const [scenario, setScenario] = useState<(typeof scenarios)[number]>("Base market");
  const [view, setView] = useState<"history" | "forecast">("forecast");

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Market intelligence</p>
            <h1>Freight outlook</h1>
            <p>Compare route and vessel-class conditions without hiding forecast uncertainty.</p>
          </div>
          <StatusBadge status="ESTIMATED" />
        </header>

        <section className="glass-panel filter-bar" aria-label="Forecast controls">
          <label>
            Route
            <Select aria-label="Route selector" defaultValue="">
              <option value="">Select route</option>
            </Select>
          </label>
          <label>
            Vessel class
            <Select aria-label="Vessel class selector" defaultValue="">
              <option value="">Select class</option>
            </Select>
          </label>
          <label>
            Horizon
            <Select
              aria-label="Forecast horizon"
              value={horizon}
              onChange={(event) =>
                setHorizon(Number(event.target.value) as (typeof forecastHorizonOptions)[number])
              }
            >
              {forecastHorizonOptions.map((days) => (
                <option key={days} value={days}>
                  {days} days
                </option>
              ))}
            </Select>
          </label>
          <label>
            Scenario overlay
            <Select
              aria-label="Scenario overlay"
              value={scenario}
              onChange={(event) => setScenario(event.target.value as (typeof scenarios)[number])}
            >
              {scenarios.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </Select>
          </label>
        </section>

        <section className="metric-grid" aria-label="Forecast summary">
          <MetricCard label="Horizon" value={`${horizon}d`} hint="Selected forecast window" />
          <MetricCard label="Market regime" value="—" hint="Awaiting regime signal" />
          <MetricCard label="Volatility" value="—" hint="Requires historical observations" />
          <MetricCard label="Model confidence" value="—" hint="No forecast run" />
        </section>

        <section className="panel-grid">
          <ChartContainer title="Historical freight and forecast">
            <div className="toggle-bar" role="group" aria-label="Freight view">
              <button
                type="button"
                className={view === "history" ? "primary" : undefined}
                onClick={() => setView("history")}
              >
                Historical
              </button>
              <button
                type="button"
                className={view === "forecast" ? "primary" : undefined}
                onClick={() => setView("forecast")}
              >
                Forecast
              </button>
            </div>
            <EmptyState
              title={
                view === "history" ? "Historical observations required" : "Forecast unavailable"
              }
            />
            <p className="chart-note">
              {view === "forecast"
                ? "Forecasts will display point estimates with p10–p90 uncertainty bands."
                : "Historical rates are supplied to the forecast endpoint by the selected decision session."}
            </p>
          </ChartContainer>
          <section className="glass-panel">
            <h2>Uncertainty range</h2>
            <div className="uncertainty-legend" aria-label="Forecast interval legend">
              <span>
                <i className="legend-dot legend-dot--p10" />
                P10 lower outcome
              </span>
              <span>
                <i className="legend-dot legend-dot--p50" />
                P50 midpoint
              </span>
              <span>
                <i className="legend-dot legend-dot--p90" />
                P90 upper outcome
              </span>
            </div>
            <p className="lede">
              Intervals communicate a range of outcomes, not a guaranteed rate.
            </p>
            <StatusBadge status="ESTIMATED" />
          </section>
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Drivers and shock indicators</h2>
            <ul className="data-list">
              <li>
                <strong>Forecast drivers</strong>
                <span>Awaiting model output</span>
              </li>
              <li>
                <strong>Market shocks</strong>
                <span>Not evaluated</span>
              </li>
              <li>
                <strong>Overlay</strong>
                <span>{scenario}</span>
              </li>
            </ul>
          </section>
          <section className="glass-panel">
            <h2>Model metadata</h2>
            <ul className="data-list">
              <li>
                <strong>Model version</strong>
                <span>—</span>
              </li>
              <li>
                <strong>Calibration</strong>
                <span>Insufficient history</span>
              </li>
              <li>
                <strong>Data freshness</strong>
                <span>DEMO</span>
              </li>
            </ul>
          </section>
        </section>
      </main>
    </Shell>
  );
}
