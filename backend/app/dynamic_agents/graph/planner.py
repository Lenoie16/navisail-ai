"""Question decomposition and approved capability planning."""

from app.copilot.registry import TOOL_NAMES
from app.dynamic_agents.shared.models import AgentPlan

_KEYWORDS = {
    "shipment": "get_shipment",
    "state": "get_maritime_state",
    "freight": "get_freight_forecast",
    "forecast": "get_freight_forecast",
    "vessel": "get_vessel_candidates",
    "port": "check_port_compatibility",
    "berth": "check_port_compatibility",
    "congestion": "get_congestion",
    "cost": "calculate_landed_cost",
    "booking": "compare_booking_dates",
    "contract": "compare_contract_strategies",
    "risk": "run_monte_carlo",
    "inventory": "get_inventory_risk",
    "recommend": "get_recommendation",
    "explain": "get_decision_explanation",
}


def plan_question(question: str) -> AgentPlan:
    normalized = question.lower()
    tools = tuple(dict.fromkeys(tool for word, tool in _KEYWORDS.items() if word in normalized))
    missing = () if tools else ("approved capability for this question",)
    return AgentPlan(
        tools=tuple(tool for tool in tools if tool in TOOL_NAMES),
        missing_capabilities=missing,
        rationale="Decomposed question into approved retrieval and analysis tools.",
    )


__all__ = ["plan_question"]
