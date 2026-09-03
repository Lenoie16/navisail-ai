"""Transparent charter-now versus wait economics."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TimingDecision = Literal["Charter Now", "Wait", "Neutral/Indeterminate"]


class CurrentBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_date: date
    freight_cost: float = Field(ge=0)
    landed_cost: float = Field(ge=0)
    vessel_availability_risk: float = Field(default=0, ge=0, le=1)
    port_congestion_impact: float = Field(default=0, ge=0)
    delay_risk: float = Field(default=0, ge=0, le=1)
    confidence: float = Field(default=1, ge=0, le=1)


class BookingCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    booking_date: date
    expected_freight_cost: float = Field(ge=0)
    expected_landed_cost: float = Field(ge=0)
    freight_p10: float = Field(ge=0)
    freight_p50: float = Field(ge=0)
    freight_p90: float = Field(ge=0)
    delay_risk: float = Field(default=0, ge=0, le=1)
    vessel_availability_risk: float = Field(default=0, ge=0, le=1)
    port_congestion_impact: float = Field(default=0, ge=0)
    inventory_exposure: float = Field(default=0, ge=0)
    disruption_probability: float = Field(default=0, ge=0, le=1)
    disruption_cost: float = Field(default=0, ge=0)
    contract_savings: float = Field(default=0, ge=0)
    confidence: float = Field(default=1, ge=0, le=1)
    assumptions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def ordered_quantiles(self) -> BookingCandidate:
        if not self.freight_p10 <= self.freight_p50 <= self.freight_p90:
            raise ValueError("freight quantiles must be ordered")
        return self


class WaitingCost(BaseModel):
    future_expected_economic_change: float
    increased_operational_risk: float
    inventory_exposure: float
    probability_weighted_disruption: float
    total: float
    assumptions: tuple[str, ...]


class TimingEvaluation(BaseModel):
    booking_date: date
    expected_freight_cost: float
    expected_landed_cost: float
    delay_impact: float
    inventory_impact: float
    stockout_exposure: float
    vessel_availability_risk: float
    port_congestion_impact: float
    downside_risk: float
    waiting_cost: WaitingCost
    net_advantage_vs_now: float
    assumptions: tuple[str, ...]


class CharterDecision(BaseModel):
    decision: TimingDecision
    recommended_booking_window: tuple[date, date]
    expected_savings: float
    waiting_cost: float
    downside_risk: float
    confidence: float = Field(ge=0, le=1)
    now: TimingEvaluation
    evaluations: tuple[TimingEvaluation, ...]
    explanation: str


class CharterTimingEngine:
    """Compare booking dates; forecast inputs remain assumptions, not certainty."""

    def evaluate(
        self,
        current: CurrentBooking,
        candidates: Iterable[BookingCandidate],
        *,
        risk_cost_per_unit: float = 1,
        neutral_threshold: float = 0.02,
    ) -> CharterDecision:
        if risk_cost_per_unit < 0 or neutral_threshold < 0:
            raise ValueError("risk_cost_per_unit and neutral_threshold must be non-negative")
        candidate_list = sorted(candidates, key=lambda item: item.booking_date)
        now_waiting = WaitingCost(
            future_expected_economic_change=0,
            increased_operational_risk=0,
            inventory_exposure=0,
            probability_weighted_disruption=0,
            total=0,
            assumptions=("current booking is the comparison baseline",),
        )
        now = self._evaluation(
            current.booking_date,
            current.freight_cost,
            current.landed_cost,
            current.delay_risk,
            current.vessel_availability_risk,
            current.port_congestion_impact,
            0,
            current.delay_risk * risk_cost_per_unit,
            now_waiting,
            0,
            ("current landed cost is the baseline",),
        )
        evaluations = tuple(
            self._candidate_evaluation(current, item, risk_cost_per_unit)
            for item in candidate_list
        )
        best = min(evaluations, key=lambda item: item.waiting_cost.total)
        advantage = best.net_advantage_vs_now
        if abs(advantage) <= neutral_threshold * max(current.landed_cost, 1):
            decision: TimingDecision = "Neutral/Indeterminate"
        elif advantage > 0:
            decision = "Wait"
        else:
            decision = "Charter Now"
        confidence = max(0.1, min(
            current.confidence,
            best.waiting_cost.total
            and best.waiting_cost.total
            / max(best.expected_landed_cost + best.waiting_cost.total, 1)
            or current.confidence,
        ))
        window = (best.booking_date, best.booking_date)
        explanation = self._explanation(decision, best, advantage)
        return CharterDecision(
            decision=decision,
            recommended_booking_window=window,
            expected_savings=abs(advantage) if decision != "Neutral/Indeterminate" else 0,
            waiting_cost=best.waiting_cost.total,
            downside_risk=best.downside_risk,
            confidence=confidence,
            now=now,
            evaluations=evaluations,
            explanation=explanation,
        )

    def _candidate_evaluation(
        self, current: CurrentBooking, candidate: BookingCandidate, risk_cost_per_unit: float
    ) -> TimingEvaluation:
        economic_change = (
            candidate.expected_landed_cost
            - current.landed_cost
            - candidate.contract_savings
        )
        operational = (
            candidate.delay_risk
            + candidate.vessel_availability_risk
            + candidate.port_congestion_impact
            - current.delay_risk
            - current.vessel_availability_risk
            - current.port_congestion_impact
        ) * risk_cost_per_unit
        disruption = candidate.disruption_probability * candidate.disruption_cost
        waiting = WaitingCost(
            future_expected_economic_change=economic_change,
            increased_operational_risk=operational,
            inventory_exposure=candidate.inventory_exposure,
            probability_weighted_disruption=disruption,
            total=economic_change + operational + candidate.inventory_exposure + disruption,
            assumptions=candidate.assumptions + ("disruption is probability weighted",),
        )
        downside = max(0, candidate.freight_p90 - candidate.freight_p50) + disruption
        return self._evaluation(
            candidate.booking_date,
            candidate.expected_freight_cost,
            candidate.expected_landed_cost,
            candidate.delay_risk,
            candidate.vessel_availability_risk,
            candidate.port_congestion_impact,
            candidate.inventory_exposure,
            downside,
            waiting,
            -waiting.total,
            candidate.assumptions,
        )

    @staticmethod
    def _evaluation(
        booking_date: date,
        freight: float,
        landed: float,
        delay: float,
        availability: float,
        congestion: float,
        inventory: float,
        downside: float,
        waiting: WaitingCost,
        advantage: float,
        assumptions: tuple[str, ...],
    ) -> TimingEvaluation:
        return TimingEvaluation(
            booking_date=booking_date,
            expected_freight_cost=freight,
            expected_landed_cost=landed,
            delay_impact=delay,
            inventory_impact=inventory,
            stockout_exposure=min(1, inventory / max(landed, 1)),
            vessel_availability_risk=availability,
            port_congestion_impact=congestion,
            downside_risk=downside,
            waiting_cost=waiting,
            net_advantage_vs_now=advantage,
            assumptions=assumptions,
        )

    @staticmethod
    def _explanation(decision: TimingDecision, best: TimingEvaluation, advantage: float) -> str:
        if decision == "Wait":
            return (
                f"Wait until {best.booking_date}: modeled waiting economics improve "
                f"the comparison by {advantage:.2f}."
            )
        if decision == "Charter Now":
            return f"Charter now: waiting has modeled net cost of {abs(advantage):.2f}."
        return (
            "The modeled timing difference is within the neutral threshold; evidence "
            "is insufficient for a timing preference."
        )


timing_engine = CharterTimingEngine()

__all__ = [
    "BookingCandidate",
    "CharterDecision",
    "CharterTimingEngine",
    "CurrentBooking",
    "TimingDecision",
    "TimingEvaluation",
    "WaitingCost",
    "timing_engine",
]