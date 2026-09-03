"""Typed copilot tool contracts."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ToolName = Literal[
    "get_shipment",
    "get_maritime_state",
    "get_freight_forecast",
    "get_vessel_candidates",
    "check_port_compatibility",
    "get_congestion",
    "calculate_landed_cost",
    "compare_booking_dates",
    "compare_contract_strategies",
    "run_monte_carlo",
    "get_inventory_risk",
    "get_recommendation",
    "get_decision_explanation",
]


class CopilotSession(BaseModel):
    """Conversation context and immutable numerical artifacts."""

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    source_state_snapshot: str = Field(min_length=1)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: ToolName
    arguments: dict[str, Any] = Field(default_factory=dict)
    session: CopilotSession


class ToolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    tool: ToolName
    session_id: str
    source: str
    source_state_snapshot: str
    data: Any = None
    error_code: str | None = None
    error_message: str | None = None


__all__ = ["CopilotSession", "ToolCall", "ToolName", "ToolResponse"]
