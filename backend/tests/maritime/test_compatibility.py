from datetime import UTC, datetime

from app.maritime.compatibility.service import (
    BerthCapability,
    CargoConstraints,
    CompatibilityEngine,
    DynamicConstraints,
    PortCapability,
    VesselTechnicalProfile,
)


def _vessel(**overrides: object) -> VesselTechnicalProfile:
    values: dict[str, object] = {
        "vessel_id": "v-1",
        "name": "Aurora",
        "loa_m": 200,
        "beam_m": 32,
        "draft_m": 12,
        "dwt_tonnes": 80_000,
        "cargo_capabilities": frozenset({"dry_bulk"}),
    }
    values.update(overrides)
    return VesselTechnicalProfile(**values)


def _port(**overrides: object) -> PortCapability:
    values: dict[str, object] = {
        "port_id": "p-1",
        "name": "Harbor",
        "channel_max_loa_m": 220,
        "channel_max_beam_m": 35,
        "channel_max_draft_m": 13,
        "channel_max_dwt_tonnes": 100_000,
        "cargo_capabilities": frozenset({"dry_bulk"}),
    }
    values.update(overrides)
    return PortCapability(**values)


def _cargo() -> CargoConstraints:
    return CargoConstraints(
        cargo_type="iron_ore", quantity_tonnes=50_000, required_capabilities=frozenset({"dry_bulk"})
    )


def test_oversized_and_excessive_draft_are_hard_failures() -> None:
    result = CompatibilityEngine().check(
        _vessel(loa_m=240, draft_m=14), _port(), _cargo()
    )

    assert result.feasible is False
    assert "LOA exceeds channel limit" in result.hard_failures
    assert "draft exceeds channel limit" in result.hard_failures
    assert result.penalty == float("inf")


def test_incorrect_cargo_capability_excludes_vessel() -> None:
    result = CompatibilityEngine().check(_vessel(cargo_capabilities=frozenset()), _port(), _cargo())

    assert result.feasible is False
    assert "vessel lacks cargo capabilities: dry_bulk" in result.hard_failures


def test_closed_berth_and_dynamic_depth_are_hard_failures() -> None:
    berth = BerthCapability(
        berth_id="b-1",
        name="Closed berth",
        max_draft_m=13,
        dynamic=DynamicConstraints(berth_closed=True),
    )
    port = _port(berths=(berth,), dynamic=DynamicConstraints(water_depth_m=10))

    result = CompatibilityEngine().check(_vessel(), port, _cargo(), berth)

    assert result.feasible is False
    assert "draft exceeds current water depth" in result.hard_failures
    assert "berth is closed" in result.hard_failures
    assert result.berth_level_compatibility is False


def test_borderline_dimensions_are_feasible_and_matrix_is_berth_level() -> None:
    berth = BerthCapability(
        berth_id="b-1",
        name="Borderline",
        max_loa_m=200,
        max_beam_m=32,
        max_draft_m=12,
        cargo_capabilities=frozenset({"dry_bulk"}),
    )
    port = _port(berths=(berth,))
    engine = CompatibilityEngine()

    result = engine.check(_vessel(), port, _cargo(), berth)

    assert result.feasible is True
    assert result.berth_level_compatibility is True
    assert engine.berth_candidate_matrix(_vessel(), port, _cargo())["b-1"].feasible is True


def test_temporal_restriction_is_a_hard_failure() -> None:
    port = _port(
        dynamic=DynamicConstraints(
            available_from=datetime(2026, 2, 1, tzinfo=UTC),
        )
    )

    result = CompatibilityEngine().check(
        _vessel(), port, _cargo(), at=datetime(2026, 1, 1, tzinfo=UTC)
    )

    assert result.feasible is False
    assert "operation falls outside temporal availability window" in result.hard_failures