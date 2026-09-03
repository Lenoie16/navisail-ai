"""Central numerical recommendation pipeline."""

from __future__ import annotations

import hashlib
import json

from app.optimization.service import OptimizationService
from app.recommendations.recommendation import (
    DecisionSessionInput,
    Recommendation,
    RecommendationAlternative,
)


class RecommendationEngine:
    """Orchestrate existing engines without mutating their inputs."""

    def __init__(self, optimization: OptimizationService | None = None) -> None:
        self.optimization = optimization or OptimizationService()

    def recommend(self, session: DecisionSessionInput) -> Recommendation:
        result = self.optimization.optimize(session.optimization_problem)
        alternatives = tuple(
            self._alternative(item, session) for item in result.alternatives
        )
        if result.solution is None:
            return Recommendation(
                decision="No Feasible Alternative",
                preferred_strategy=session.preferred_strategy,
                preferred_vessel=None,
                preferred_port=None,
                preferred_berth=None,
                preferred_booking_timing=None,
                preferred_contract=session.preferred_contract,
                expected_landed_cost=None,
                risk_adjusted_cost=None,
                expected_arrival=None,
                delay_risk=None,
                inventory_impact=None,
                confidence=0,
                alternatives=alternatives,
                key_assumptions=self._assumptions(session),
                main_drivers=("no candidate satisfies hard constraints",),
                major_downside_scenarios=tuple(result.hard_constraints),
                source_state_snapshot=str(session.maritime_state.snapshot_id),
                model_versions=session.model_versions,
                parameter_version=session.parameter_version,
                reproducibility_key=self._key(session),
                explanation=result.explanation,
            )
        selected = self._alternative(result.solution, session)
        data_confidence = min(
            (component.quality for component in session.maritime_state.components.values()),
            default=0,
        )
        decision_confidence = max(0, min(1, 1 - selected.delay_risk))
        return Recommendation(
            decision="Recommended",
            preferred_strategy=session.preferred_strategy,
            preferred_vessel=selected.vessel_id,
            preferred_port=selected.port_id,
            preferred_berth=selected.berth_id,
            preferred_booking_timing=selected.expected_arrival,
            preferred_contract=session.preferred_contract,
            expected_landed_cost=selected.expected_landed_cost,
            risk_adjusted_cost=selected.risk_adjusted_cost,
            expected_arrival=selected.expected_arrival,
            delay_risk=selected.delay_risk,
            inventory_impact=selected.inventory_impact,
            confidence=decision_confidence,
            data_confidence=data_confidence,
            model_confidence=decision_confidence,
            decision_confidence=decision_confidence,
            alternatives=alternatives,
            key_assumptions=self._assumptions(session),
            main_drivers=(
                "hard feasibility constraints",
                "risk-adjusted optimization objective",
                "inventory continuity metadata",
            ),
            major_downside_scenarios=tuple(
                name for name, value in session.risk.items() if value
            ),
            source_state_snapshot=str(session.maritime_state.snapshot_id),
            model_versions=session.model_versions,
            parameter_version=session.parameter_version,
            reproducibility_key=self._key(session),
            explanation=result.explanation,
        )

    @staticmethod
    def _alternative(option, session: DecisionSessionInput) -> RecommendationAlternative:
        delay_risk = min(
            1,
            option.penalties.get("schedule_reliability", 0)
            + option.penalties.get("congestion", 0),
        )
        inventory_impact = float(
            session.inventory.get(
                option.option_id, session.inventory.get("stockout_probability", 0)
            )
        )
        return RecommendationAlternative(
            option_id=option.option_id,
            vessel_id=option.vessel_id,
            port_id=option.port_id,
            berth_id=option.berth_id,
            route_id=option.route_id,
            expected_landed_cost=option.expected_cost,
            risk_adjusted_cost=option.objective_value,
            expected_arrival=next(
                item.available_at
                for item in session.optimization_problem.options
                if item.option_id == option.option_id
            ),
            delay_risk=delay_risk,
            inventory_impact=inventory_impact,
            explanation=option.explanation,
        )

    @staticmethod
    def _assumptions(session: DecisionSessionInput) -> tuple[str, ...]:
        return (
            "recommendation is reproducible from the supplied state snapshot",
            "upstream numerical engines are treated as inputs",
            f"parameter version: {session.parameter_version}",
        )

    @staticmethod
    def _key(session: DecisionSessionInput) -> str:
        payload = {
            "snapshot": str(session.maritime_state.snapshot_id),
            "problem": session.optimization_problem.model_dump(mode="json"),
            "model_versions": session.model_versions,
            "parameter_version": session.parameter_version,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


recommendation_engine = RecommendationEngine()

__all__ = ["RecommendationEngine", "recommendation_engine"]
