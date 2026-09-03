import type { RiskScenario, SimulationAlternative } from "../lib/api";

export type ScenarioControl =
  | "freightSpike"
  | "congestion"
  | "portOutage"
  | "cyclone"
  | "fuelSpike"
  | "vesselFailure"
  | "delay"
  | "inventoryShock";

export type ScenarioControls = Record<ScenarioControl, number>;

export type SimulationProgress = "idle" | "running" | "complete" | "unavailable" | "failed";

export const scenarioControlLabels: Record<ScenarioControl, string> = {
  freightSpike: "Freight spike",
  congestion: "Congestion",
  portOutage: "Port outage",
  cyclone: "Cyclone / weather",
  fuelSpike: "Fuel spike",
  vesselFailure: "Vessel failure",
  delay: "Operational delay",
  inventoryShock: "Inventory shock",
};

export const defaultScenarioControls: ScenarioControls = {
  freightSpike: 0,
  congestion: 0,
  portOutage: 0,
  cyclone: 0,
  fuelSpike: 0,
  vesselFailure: 0,
  delay: 0,
  inventoryShock: 0,
};

export const normalRiskScenario: RiskScenario = {
  name: "normal",
  freight_volatility: 0.1,
  fuel_volatility: 0.1,
  congestion_probability: 0.1,
  waiting_hours: 4,
  weather_probability: 0.1,
  vessel_failure_probability: 0.02,
  port_outage_probability: 0.01,
  fx_volatility: 0.05,
  operational_delay_hours: 2,
  disruption_cost: 0,
};

export function scenarioControlsToRiskScenario(controls: ScenarioControls): RiskScenario {
  return {
    ...normalRiskScenario,
    name: "what-if",
    freight_volatility: normalRiskScenario.freight_volatility + controls.freightSpike * 0.3,
    fuel_volatility: normalRiskScenario.fuel_volatility + controls.fuelSpike * 0.3,
    congestion_probability: Math.min(
      1,
      normalRiskScenario.congestion_probability + controls.congestion,
    ),
    port_outage_probability: Math.min(
      1,
      normalRiskScenario.port_outage_probability + controls.portOutage,
    ),
    weather_probability: Math.min(1, normalRiskScenario.weather_probability + controls.cyclone),
    vessel_failure_probability: Math.min(
      1,
      normalRiskScenario.vessel_failure_probability + controls.vesselFailure,
    ),
    operational_delay_hours: normalRiskScenario.operational_delay_hours + controls.delay,
    waiting_hours: normalRiskScenario.waiting_hours + controls.congestion * 24,
    disruption_cost:
      (controls.portOutage + controls.vesselFailure) * normalRiskScenario.disruption_cost,
  };
}

export function cloneAlternative(alternative: SimulationAlternative): SimulationAlternative {
  return { ...alternative };
}

export type ScenariosState = {
  selected?: string;
  baselineProgress: SimulationProgress;
  scenarioProgress: SimulationProgress;
};
