"""Explainability and decision memo contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.recommendations.recommendation import Recommendation


class ExplainabilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation: Recommendation


class Counterfactual(BaseModel):
    option_id: str
    statement: str
    additional_risk_adjusted_cost: float
    additional_delay_risk: float
    changed_inventory_exposure: float
    changed_feasibility: bool = False


class DecisionMemo(BaseModel):
    decision: str
    executive_recommendation: str
    rationale: tuple[str, ...]
    key_numbers: dict[str, float | str | datetime | None]
    alternatives: tuple[Counterfactual, ...]
    risks: tuple[str, ...]
    assumptions: tuple[str, ...]
    recommended_action: str
    approval_requirement: str
    data_confidence: float = Field(ge=0, le=1)
    model_confidence: float = Field(ge=0, le=1)
    decision_confidence: float = Field(ge=0, le=1)
    source_state_snapshot: str
    model_versions: dict[str, str]
    parameter_version: str
    reproducibility_key: str


__all__ = ["Counterfactual", "DecisionMemo", "ExplainabilityRequest"]
