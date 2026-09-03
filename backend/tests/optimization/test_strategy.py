from app.optimization.strategy import StrategyOptimizer, VoyageDemand


def _voyage() -> VoyageDemand:
    return VoyageDemand(
        voyage_id="v-1",
        volume_tonnes=10_000,
        spot_p10=90,
        spot_p50=100,
        spot_p90=110,
        coa_rate=102,
        time_charter_rate=105,
        spot_reliability=0.7,
    )


def test_stable_market_ranks_low_expected_cost_strategy() -> None:
    result = StrategyOptimizer().optimize([_voyage()])

    assert result.recommended_strategy == "Spot"
    assert result.total_volume_tonnes == 10_000
    assert result.alternatives[0].expected_cost > 0


def test_volatile_market_can_rank_coa_above_spot() -> None:
    result = StrategyOptimizer().optimize(
        [_voyage()],
        market_condition="volatile",
        constraints={"risk_tolerance": 0.2},
    )

    assert result.recommended_strategy in {"COA", "Hybrid", "Time Charter"}
    assert result.alternatives[0].risk <= 0.2


def test_rising_and_falling_markets_change_strategy_economics() -> None:
    optimizer = StrategyOptimizer()
    rising = optimizer.optimize([_voyage()], market_condition="rising")
    falling = optimizer.optimize([_voyage()], market_condition="falling")

    assert rising.expected_cost != falling.expected_cost
    assert rising.recommended_strategy != falling.recommended_strategy


def test_hybrid_and_multi_voyage_allocation_are_returned() -> None:
    result = StrategyOptimizer().optimize(
        [_voyage(), _voyage().model_copy(update={"voyage_id": "v-2", "volume_tonnes": 20_000})],
        constraints={"minimum_coa_share": 0.2, "maximum_time_charter_share": 0.5},
    )

    assert result.total_volume_tonnes == 30_000
    assert any(item.strategy == "Hybrid" for item in result.alternatives)
    assert sum(result.recommended_allocation.values()) == 1


def test_high_inventory_pressure_rewards_reliability() -> None:
    optimizer = StrategyOptimizer()
    normal = optimizer.optimize([_voyage()])
    pressured = optimizer.optimize(
        [_voyage()], constraints={"inventory_pressure": 1, "risk_tolerance": 1}
    )

    assert normal.recommended_strategy != pressured.recommended_strategy