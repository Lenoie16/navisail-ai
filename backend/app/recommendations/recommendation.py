"""Unified recommendation contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from app.maritime.state_vector import MaritimeStateVector
from app.optimization.models import OptimizationProblem
from pydantic import BaseModel, ConfigDict, Field


class DecisionSessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    maritime_state: MaritimeStateVector
    optimization_problem: OptimizationProblem
    preferred_strategy: str = "Spot"
    preferred_contract: str | None = None
    forecast: dict[str, Any] = Field(default_factory=dict)
    congestion: dict[str, Any] = Field(default_factory=dict)
    landed_cost: dict[str, Any] = Field(default_factory=dict)
    timing: dict[str, Any] = Field(default_factory=dict)
    contract_alternatives: tuple[str, ...] = ()
    risk: dict[str, Any] = Field(default_factory=dict)
    inventory: dict[str, Any] = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)
    parameter_version: str = "recommendation-v1"


class RecommendationAlternative(BaseModel):
    option_id: str
    vessel_id: str
    port_id: str
    berth_id: str
    route_id: str
    expected_landed_cost: float
    risk_adjusted_cost: float
    expected_arrival: datetime
    delay_risk: float
    inventory_impact: float
    explanation: str


class Recommendation(BaseModel):
    decision: Literal["Recommended", "No Feasible Alternative"]
    preferred_strategy: str
    preferred_vessel: str | None
    preferred_port: str | None
    preferred_berth: str | None
    preferred_booking_timing: datetime | None
    preferred_contract: str | None
    expected_landed_cost: float | None
    risk_adjusted_cost: float | None
    expected_arrival: datetime | None
    delay_risk: float | None
    inventory_impact: float | None
    confidence: float = Field(ge=0, le=1)
    data_confidence: float = Field(default=0, ge=0, le=1)
    model_confidence: float = Field(default=0, ge=0, le=1)
    decision_confidence: float = Field(default=0, ge=0, le=1)
    alternatives: tuple[RecommendationAlternative, ...]
    key_assumptions: tuple[str, ...]
    main_drivers: tuple[str, ...]
    major_downside_scenarios: tuple[str, ...]
    source_state_snapshot: str
    model_versions: dict[str, str]
    parameter_version: str
    reproducibility_key: str
    explanation: str


__all__ = ["DecisionSessionInput", "Recommendation", "RecommendationAlternative"]
