"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import {
  ChartContainer,
  ErrorState,
  LoadingState,
  MetricCard,
  StatusBadge,
} from "../../components/ui";
import {
  type StrategyOptimizationResult,
  type StrategyRequest,
  optimizeStrategy,
} from "../../lib/api";
import { validateStrategyRequest } from "../../lib/contracts";

const strategies = ["Spot", "COA", "Time Charter", "Hybrid"] as const;

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export default function ContractsPage() {
  const [volume, setVolume] = useState("50000");
  const [market, setMarket] = useState<StrategyRequest["market_condition"]>("stable");
  const [risk, setRisk] = useState("0.5");
  const [voyages, setVoyages] = useState("1");
  const [spotP10, setSpotP10] = useState("");
  const [spotP50, setSpotP50] = useState("");
  const [spotP90, setSpotP90] = useState("");
  const [coaRate, setCoaRate] = useState("");
  const [timeCharterRate, setTimeCharterRate] = useState("");
  const [minimumCoa, setMinimumCoa] = useState("0");
  const [maximumTimeCharter, setMaximumTimeCharter] = useState("1");
  const [result, setResult] = useState<StrategyOptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSimulation() {
    if (
      ![volume, spotP10, spotP50, spotP90, coaRate, timeCharterRate].every(
        (value) => Number(value) > 0,
      )
    ) {
      setError("Enter positive volume and authoritative rate assumptions before running.");
      return;
    }
    if (!(Number(spotP10) <= Number(spotP50) && Number(spotP50) <= Number(spotP90))) {
      setError("Spot P10, P50, and P90 must be ordered.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const request: StrategyRequest = {
        voyages: Array.from({ length: Math.max(1, Number(voyages) || 1) }, (_, index) => ({
          voyage_id: `voyage-${index + 1}`,
          volume_tonnes: Number(volume),
          spot_p10: Number(spotP10),
          spot_p50: Number(spotP50),
          spot_p90: Number(spotP90),
          coa_rate: Number(coaRate),
          time_charter_rate: Number(timeCharterRate),
        })),
        market_condition: market,
        constraints: {
          risk_tolerance: Number(risk),
          minimum_coa_share: Number(minimumCoa),
          maximum_time_charter_share: Number(maximumTimeCharter),
        },
      };
      const validationError = validateStrategyRequest(request);
      if (validationError) throw new Error(validationError);
      setResult(await optimizeStrategy(request));
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "Strategy simulation failed.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell sessionId="default">
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">Contract strategy</p>
            <h1>Contract simulator</h1>
            <p>Compare procurement strategies using the authoritative optimization service.</p>
          </div>
          <StatusBadge status={result ? "ESTIMATED" : "DEMO"} />
        </header>
        <section
          className="glass-panel simulator-controls"
          aria-label="Contract simulator controls"
        >
          <label>
            Volume per voyage
            <input
              type="number"
              min="1"
              value={volume}
              onChange={(event) => setVolume(event.target.value)}
            />
          </label>
          <label>
            Number of voyages
            <input
              type="number"
              min="1"
              value={voyages}
              onChange={(event) => setVoyages(event.target.value)}
            />
          </label>
          <label>
            Market assumption
            <select
              value={market}
              onChange={(event) =>
                setMarket(event.target.value as StrategyRequest["market_condition"])
              }
            >
              {["stable", "rising", "falling", "volatile"].map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            Risk tolerance
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={risk}
              onChange={(event) => setRisk(event.target.value)}
            />
          </label>
          <label>
            Spot P10
            <input
              type="number"
              min="0"
              value={spotP10}
              onChange={(event) => setSpotP10(event.target.value)}
            />
          </label>
          <label>
            Spot P50
            <input
              type="number"
              min="0"
              value={spotP50}
              onChange={(event) => setSpotP50(event.target.value)}
            />
          </label>
          <label>
            Spot P90
            <input
              type="number"
              min="0"
              value={spotP90}
              onChange={(event) => setSpotP90(event.target.value)}
            />
          </label>
          <label>
            COA rate
            <input
              type="number"
              min="0"
              value={coaRate}
              onChange={(event) => setCoaRate(event.target.value)}
            />
          </label>
          <label>
            Time Charter rate
            <input
              type="number"
              min="0"
              value={timeCharterRate}
              onChange={(event) => setTimeCharterRate(event.target.value)}
            />
          </label>
          <label>
            Minimum COA share
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={minimumCoa}
              onChange={(event) => setMinimumCoa(event.target.value)}
            />
          </label>
          <label>
            Maximum Time Charter share
            <input
              type="number"
              min="0"
              max="1"
              step="0.1"
              value={maximumTimeCharter}
              onChange={(event) => setMaximumTimeCharter(event.target.value)}
            />
          </label>
          <button className="primary" type="button" onClick={runSimulation} disabled={loading}>
            Run comparison
          </button>
        </section>
        {loading && <LoadingState />}
        {error && <ErrorState message={error} />}
        {!loading && !result && !error && (
          <section className="glass-panel">
            <h2>Ready for a strategy comparison</h2>
            <p className="muted-copy">
              Enter planning assumptions and run the backend optimization. No contract values are
              calculated in the browser.
            </p>
          </section>
        )}
        {result && (
          <>
            <section className="metric-grid" aria-label="Recommended strategy summary">
              <MetricCard
                label="Recommended"
                value={result.recommended_strategy}
                hint={result.explanation}
              />
              <MetricCard
                label="Expected cost"
                value={result.expected_cost.toLocaleString()}
                hint="Backend output"
              />
              <MetricCard
                label="Total volume"
                value={`${result.total_volume_tonnes.toLocaleString()} t`}
                hint="Backend output"
              />
              <MetricCard
                label="Market"
                value={result.market_condition}
                hint="Applied assumption"
              />
            </section>
            <section className="panel-grid">
              <ChartContainer title="Strategy comparison">
                <div className="strategy-grid">
                  {result.alternatives.map((alternative) => (
                    <article
                      className={
                        alternative.strategy === result.recommended_strategy
                          ? "strategy-card strategy-card--recommended"
                          : "strategy-card"
                      }
                      key={alternative.strategy}
                    >
                      <div className="strategy-card__heading">
                        <h3>{alternative.strategy}</h3>
                        {alternative.strategy === result.recommended_strategy && (
                          <StatusBadge status="ESTIMATED" />
                        )}
                      </div>
                      <MetricCard
                        label="Expected cost"
                        value={alternative.expected_cost.toLocaleString()}
                      />
                      <MetricCard
                        label="Risk-adjusted objective"
                        value={alternative.objective_value.toLocaleString()}
                      />
                      <dl className="strategy-details">
                        <div>
                          <dt>Downside</dt>
                          <dd>{alternative.downside_exposure.toLocaleString()}</dd>
                        </div>
                        <div>
                          <dt>Risk</dt>
                          <dd>{percent(alternative.risk)}</dd>
                        </div>
                        <div>
                          <dt>Flexibility</dt>
                          <dd>{percent(alternative.flexibility)}</dd>
                        </div>
                        <div>
                          <dt>Schedule reliability</dt>
                          <dd>{percent(alternative.schedule_reliability)}</dd>
                        </div>
                      </dl>
                      <p className="muted-copy">{alternative.justification}</p>
                    </article>
                  ))}
                </div>
              </ChartContainer>
              <section className="glass-panel">
                <h2>Allocation and coverage</h2>
                <ul className="data-list">
                  {strategies.map((strategy) => (
                    <li key={strategy}>
                      <strong>{strategy}</strong>
                      <span>{percent(result.recommended_allocation[strategy] ?? 0)}</span>
                    </li>
                  ))}
                </ul>
                <p className="muted-copy">
                  Volume coverage and strategy weighting are represented by the backend allocation.
                  No client-side re-ranking is applied.
                </p>
              </section>
            </section>
          </>
        )}
      </main>
    </Shell>
  );
}
