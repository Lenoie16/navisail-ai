"use client";

import { useMemo, useState } from "react";
import { Shell } from "../../components/layout";
import { Button, ErrorState, MetricCard, Select, StatusBadge } from "../../components/ui";
import { compareRisk, type RiskCompareResponse, type SimulationAlternative } from "../../lib/api";
import {
  cloneAlternative,
  defaultScenarioControls,
  scenarioControlLabels,
  scenarioControlsToRiskScenario,
  type ScenarioControl,
  type ScenarioControls,
  type SimulationProgress,
} from "../../state/scenarios";

const baselineAlternative: SimulationAlternative = {
  alternative_id: "selected-route",
  base_cost: 100000,
  base_delay_hours: 0,
  inventory_breach_threshold_hours: 24,
  cost_threshold: 120000,
  freight_exposure: 1,
  fuel_exposure: 0,
  fx_exposure: 0,
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function ProgressState({ label, state }: { label: string; state: SimulationProgress }) {
  const copy = {
    idle: "Ready",
    running: "Running",
    complete: "Complete",
    unavailable: "Unavailable",
    failed: "Failed",
  }[state];
  return (
    <span aria-label={`${label}: ${copy}`} className="chart-note">
      {label}: {copy}
    </span>
  );
}

export default function RiskPage() {
  const [controls, setControls] = useState<ScenarioControls>(defaultScenarioControls);
  const [baseline, setBaseline] = useState<RiskCompareResponse | null>(null);
  const [scenario, setScenario] = useState<RiskCompareResponse | null>(null);
  const [baselineProgress, setBaselineProgress] = useState<SimulationProgress>("idle");
  const [scenarioProgress, setScenarioProgress] = useState<SimulationProgress>("idle");
  const [error, setError] = useState<string | null>(null);

  const scenarioRequest = useMemo(() => scenarioControlsToRiskScenario(controls), [controls]);
  const baselineOutput = baseline?.[baselineAlternative.alternative_id];
  const scenarioOutput = scenario?.[baselineAlternative.alternative_id];

  function updateControl(control: ScenarioControl, value: number) {
    setControls((current) => ({ ...current, [control]: value }));
    setScenario(null);
    setScenarioProgress("idle");
  }

  async function runSimulation() {
    setError(null);
    setBaselineProgress("running");
    setScenarioProgress("running");
    try {
      const baselineInput = cloneAlternative(baselineAlternative);
      const [baselineResult, scenarioResult] = await Promise.all([
        compareRisk({
          alternatives: [baselineInput],
          scenario: { ...scenarioRequest, name: "normal" },
          simulations: 1000,
          seed: 31,
        }),
        compareRisk({
          alternatives: [cloneAlternative(baselineAlternative)],
          scenario: scenarioRequest,
          simulations: 1000,
          seed: 31,
        }),
      ]);
      setBaseline(baselineResult);
      setScenario(scenarioResult);
      setBaselineProgress("complete");
      setScenarioProgress("complete");
    } catch (reason: unknown) {
      setBaselineProgress("failed");
      setScenarioProgress("failed");
      setError(
        reason instanceof Error ? reason.message : "Simulation failed. Retry the comparison.",
      );
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Scenario lab</p>
            <h1>Risk and what-if</h1>
            <p>Explore downside exposure without changing the baseline decision session.</p>
          </div>
          <StatusBadge status="ESTIMATED" />
        </header>

        <section className="glass-panel filter-bar" aria-label="Scenario controls">
          {Object.entries(scenarioControlLabels).map(([control, label]) => {
            const key = control as ScenarioControl;
            const unsupported = key === "inventoryShock";
            return (
              <label key={control}>
                {label}
                <Select
                  aria-label={label}
                  value={controls[key]}
                  disabled={unsupported}
                  onChange={(event) => updateControl(key, Number(event.target.value))}
                >
                  <option value={0}>None</option>
                  <option value={0.1}>Low</option>
                  <option value={0.25}>Medium</option>
                  <option value={0.5}>High</option>
                </Select>
                {unsupported && <small className="chart-note">Unsupported by current API</small>}
              </label>
            );
          })}
          <Button onClick={runSimulation} disabled={baselineProgress === "running"}>
            {baselineProgress === "running" ? "Simulating…" : "Run comparison"}
          </Button>
        </section>

        <section
          className="glass-panel progress-panel"
          aria-label="Simulation progress"
          aria-live="polite"
        >
          <ProgressState label="Baseline" state={baselineProgress} />
          <ProgressState label="What-if scenario" state={scenarioProgress} />
          <span className="chart-note">Seed 31 · 1,000 simulations · baseline preserved</span>
        </section>

        {error && (
          <section className="glass-panel">
            <ErrorState message={error} />
            <Button variant="quiet" onClick={runSimulation}>
              Retry comparison
            </Button>
          </section>
        )}

        <section className="metric-grid" aria-label="Risk comparison">
          <MetricCard
            label="Baseline cost"
            value={baselineOutput ? formatCurrency(baselineOutput.mean) : "—"}
          />
          <MetricCard
            label="Scenario cost"
            value={scenarioOutput ? formatCurrency(scenarioOutput.mean) : "—"}
          />
          <MetricCard
            label="Cost difference"
            value={
              baselineOutput && scenarioOutput
                ? formatCurrency(scenarioOutput.mean - baselineOutput.mean)
                : "—"
            }
            hint="Backend simulation output"
          />
          <MetricCard
            label="Risk difference"
            value={
              baselineOutput && scenarioOutput
                ? formatPercent(
                    scenarioOutput.probability_of_delay - baselineOutput.probability_of_delay,
                  )
                : "—"
            }
            hint="Delay probability delta"
          />
        </section>

        <section className="panel-grid">
          <section className="glass-panel">
            <h2>Baseline / scenario</h2>
            <ul className="data-list">
              <li>
                <strong>Baseline P10 / P50 / P90</strong>
                <span>
                  {baselineOutput
                    ? `${formatCurrency(baselineOutput.p10)} / ${formatCurrency(baselineOutput.p50)} / ${formatCurrency(baselineOutput.p90)}`
                    : "Awaiting simulation"}
                </span>
              </li>
              <li>
                <strong>Scenario P10 / P50 / P90</strong>
                <span>
                  {scenarioOutput
                    ? `${formatCurrency(scenarioOutput.p10)} / ${formatCurrency(scenarioOutput.p50)} / ${formatCurrency(scenarioOutput.p90)}`
                    : "Awaiting simulation"}
                </span>
              </li>
              <li>
                <strong>Mean delay difference</strong>
                <span>
                  {baselineOutput && scenarioOutput
                    ? `${(scenarioOutput.mean_delay_hours - baselineOutput.mean_delay_hours).toFixed(1)} hours`
                    : "—"}
                </span>
              </li>
              <li>
                <strong>Inventory breach difference</strong>
                <span>
                  {baselineOutput && scenarioOutput
                    ? formatPercent(
                        scenarioOutput.probability_inventory_breach -
                          baselineOutput.probability_inventory_breach,
                      )
                    : "—"}
                </span>
              </li>
            </ul>
          </section>
          <section className="glass-panel">
            <h2>Decision impact</h2>
            <ul className="data-list">
              <li>
                <strong>ETA difference</strong>
                <span>Unavailable from current simulation contract.</span>
              </li>
              <li>
                <strong>Inventory difference</strong>
                <span>Unavailable from current simulation contract.</span>
              </li>
              <li>
                <strong>Recommendation change</strong>
                <span>Unavailable from current simulation contract.</span>
              </li>
              <li>
                <strong>Scenario</strong>
                <span>{scenarioRequest.name}</span>
              </li>
            </ul>
          </section>
        </section>
      </main>
    </Shell>
  );
}
