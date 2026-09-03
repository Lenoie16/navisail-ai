"""Deterministic recommendation explanation service."""

from app.explainability.models import Counterfactual, DecisionMemo, ExplainabilityRequest


class ExplainabilityService:
    """Turn engine outputs into traceable business language."""

    def explain(self, request: ExplainabilityRequest) -> DecisionMemo:
        recommendation = request.recommendation
        selected_cost = recommendation.risk_adjusted_cost or 0
        selected_delay = recommendation.delay_risk or 0
        selected_inventory = recommendation.inventory_impact or 0
        counterfactuals = tuple(
            Counterfactual(
                option_id=alternative.option_id,
                statement=(
                    f"If {alternative.option_id} were selected, risk-adjusted cost "
                    f"would change by {alternative.risk_adjusted_cost - selected_cost:.2f}."
                ),
                additional_risk_adjusted_cost=alternative.risk_adjusted_cost - selected_cost,
                additional_delay_risk=alternative.delay_risk - selected_delay,
                changed_inventory_exposure=alternative.inventory_impact - selected_inventory,
            )
            for alternative in recommendation.alternatives
            if not (
                alternative.vessel_id == recommendation.preferred_vessel
                and alternative.port_id == recommendation.preferred_port
                and alternative.berth_id == recommendation.preferred_berth
                and alternative.expected_arrival == recommendation.expected_arrival
            )
        )
        rationale = (
            *recommendation.main_drivers,
            recommendation.explanation,
        )
        risks = recommendation.major_downside_scenarios or (
            "no additional downside scenarios supplied",
        )
        action = (
            f"Proceed with {recommendation.preferred_vessel} via "
            f"{recommendation.preferred_port}/{recommendation.preferred_berth}."
            if recommendation.decision == "Recommended"
            else "Do not approve booking until a feasible alternative is available."
        )
        return DecisionMemo(
            decision=recommendation.decision,
            executive_recommendation=recommendation.explanation,
            rationale=rationale,
            key_numbers={
                "expected_landed_cost": recommendation.expected_landed_cost,
                "risk_adjusted_cost": recommendation.risk_adjusted_cost,
                "expected_arrival": recommendation.expected_arrival,
                "delay_risk": recommendation.delay_risk,
                "inventory_impact": recommendation.inventory_impact,
            },
            alternatives=counterfactuals,
            risks=risks,
            assumptions=recommendation.key_assumptions,
            recommended_action=action,
            approval_requirement=(
                "Approval required for booking and contract commitment."
                if recommendation.decision == "Recommended"
                else "Escalation required because no feasible alternative exists."
            ),
            data_confidence=recommendation.data_confidence,
            model_confidence=recommendation.model_confidence,
            decision_confidence=recommendation.decision_confidence or recommendation.confidence,
            source_state_snapshot=recommendation.source_state_snapshot,
            model_versions=recommendation.model_versions,
            parameter_version=recommendation.parameter_version,
            reproducibility_key=recommendation.reproducibility_key,
        )


explainability_service = ExplainabilityService()

__all__ = ["ExplainabilityService", "explainability_service"]
