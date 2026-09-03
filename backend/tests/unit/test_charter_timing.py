from datetime import date

from app.charter.service import BookingCandidate, CharterTimingEngine, CurrentBooking


def _current() -> CurrentBooking:
    return CurrentBooking(
        booking_date=date(2026, 1, 1),
        freight_cost=100,
        landed_cost=1_000,
        confidence=0.9,
    )


def _candidate(**overrides: object) -> BookingCandidate:
    values: dict[str, object] = {
        "booking_date": date(2026, 1, 8),
        "expected_freight_cost": 80,
        "expected_landed_cost": 900,
        "freight_p10": 70,
        "freight_p50": 80,
        "freight_p90": 100,
        "confidence": 0.85,
    }
    values.update(overrides)
    return BookingCandidate(**values)


def test_waiting_clearly_helps() -> None:
    result = CharterTimingEngine().evaluate(_current(), [_candidate()])

    assert result.decision == "Wait"
    assert result.expected_savings > 0
    assert result.waiting_cost < 0
    assert result.evaluations[0].waiting_cost.future_expected_economic_change < 0


def test_booking_now_clearly_helps_when_waiting_adds_risk() -> None:
    result = CharterTimingEngine().evaluate(
        _current(),
        [
            _candidate(
                expected_landed_cost=1_050,
                freight_p50=120,
                freight_p90=180,
                delay_risk=0.8,
                vessel_availability_risk=0.8,
                disruption_probability=0.5,
                disruption_cost=500,
            )
        ],
    )

    assert result.decision == "Charter Now"
    assert result.waiting_cost > 0
    assert result.downside_risk >= 300


def test_nearly_tied_decision_is_indeterminate() -> None:
    result = CharterTimingEngine().evaluate(
        _current(),
        [_candidate(expected_landed_cost=1_000, expected_freight_cost=100)],
    )

    assert result.decision == "Neutral/Indeterminate"
    assert result.expected_savings == 0
    assert "neutral threshold" in result.explanation