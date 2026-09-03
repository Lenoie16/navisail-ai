from app.risk.monte_carlo import MonteCarloEngine, SimulationAlternative
from app.risk.scenarios import RiskScenario


def _alternative(alternative_id: str, **overrides: object) -> SimulationAlternative:
    values: dict[str, object] = {
        "alternative_id": alternative_id,
        "base_cost": 100_000,
        "base_delay_hours": 0,
        "inventory_breach_threshold_hours": 20,
        "cost_threshold": 120_000,
        "freight_exposure": 1,
        "fuel_exposure": 0.2,
        "fx_exposure": 0.1,
    }
    values.update(overrides)
    return SimulationAlternative(**values)


def test_fixed_seed_is_deterministic_and_has_tail_metrics() -> None:
    engine = MonteCarloEngine()
    scenario = RiskScenario(
        name="demo",
        freight_volatility=0.1,
        congestion_probability=0.2,
        waiting_hours=12,
        operational_delay_hours=4,
    )

    first = engine.simulate([_alternative("a")], scenario=scenario, simulations=500, seed=42)[0]
    second = engine.simulate([_alternative("a")], scenario=scenario, simulations=500, seed=42)[0]

    assert first == second
    assert first.p10 <= first.p50 <= first.p90
    assert first.cvar_90 >= first.p90
    assert 0 <= first.probability_of_delay <= 1


def test_comparison_uses_same_seed_and_reports_thresholds() -> None:
    scenario = RiskScenario(name="severe", congestion_probability=1, waiting_hours=30)
    outputs = MonteCarloEngine().compare(
        [_alternative("a"), _alternative("b", base_cost=110_000)],
        scenario=scenario,
        simulations=200,
        seed=7,
    )

    assert outputs["a"].seed == outputs["b"].seed == 7
    assert outputs["a"].scenario == "severe"
    assert outputs["a"].probability_exceeding_cost_threshold > 0
    assert outputs["a"].probability_inventory_breach == 1


def test_more_simulations_converge_to_stable_mean() -> None:
    engine = MonteCarloEngine()
    scenario = RiskScenario(name="normal", freight_volatility=0.05)
    small = engine.simulate([_alternative("a")], scenario=scenario, simulations=100, seed=9)[0]
    large = engine.simulate([_alternative("a")], scenario=scenario, simulations=10_000, seed=9)[0]

    assert abs(small.mean - large.mean) < 5_000