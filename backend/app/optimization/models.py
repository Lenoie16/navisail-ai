"""Typed optimization inputs and explainable solution outputs."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OptimizationOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str = Field(min_length=1)
    vessel_id: str = Field(min_length=1)
    port_id: str = Field(min_length=1)
    berth_id: str = Field(min_length=1)
    route_id: str = Field(min_length=1)
    available_at: datetime
    laycan_start: datetime | None = None
    laycan_end: datetime | None = None
    capacity_tonnes: float = Field(gt=0)
    cost_per_tonne: float = Field(ge=0)
    schedule_reliability: float = Field(default=1, ge=0, le=1)
    congestion_penalty: float = Field(default=0, ge=0)
    risk_score: float = Field(default=0, ge=0, le=1)
    stockout_probability: float = Field(default=0, ge=0, le=1)
    continuity_acceptable: bool = True
    feasible: bool = True
    hard_failures: tuple[str, ...] = ()
    soft_constraints: tuple[str, ...] = ()
    binding_constraints: tuple[str, ...] = ()
    metadata: dict[str, str | float | int] = Field(default_factory=dict)

    @model_validator(mode="after")
    def normalize_and_validate(self) -> OptimizationOption:
        if self.available_at.tzinfo is None:
            raise ValueError("available_at must include a timezone")
        self.available_at = self.available_at.astimezone(UTC)
        if self.laycan_start and self.laycan_end and self.laycan_end < self.laycan_start:
            raise ValueError("laycan_end must not precede laycan_start")
        if self.feasible and self.hard_failures:
            raise ValueError("feasible options cannot contain hard failures")
        return self


class OptimizationProblem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shipment_id: str = Field(min_length=1)
    quantity_tonnes: float = Field(gt=0)
    booking_deadline: datetime
    inventory_available_tonnes: float = Field(default=0, ge=0)
    inventory_minimum_tonnes: float = Field(default=0, ge=0)
    risk_tolerance: float = Field(default=1, ge=0, le=1)
    options: tuple[OptimizationOption, ...]

    @model_validator(mode="after")
    def valid_problem(self) -> OptimizationProblem:
        if self.booking_deadline.tzinfo is None:
            raise ValueError("booking_deadline must include a timezone")
        if self.inventory_available_tonnes - self.quantity_tonnes < self.inventory_minimum_tonnes:
            raise ValueError("shipment would breach inventory minimum")
        return self


class ConstraintStatus(BaseModel):
    name: str
    satisfied: bool
    hard: bool
    detail: str


class OptimizationSolution(BaseModel):
    option_id: str
    vessel_id: str
    port_id: str
    berth_id: str
    route_id: str
    allocated_tonnes: float
    objective_value: float
    expected_cost: float
    penalties: dict[str, float]
    constraint_status: tuple[ConstraintStatus, ...]
    binding_constraints: tuple[str, ...]
    explanation: str


class OptimizationResult(BaseModel):
    feasible: bool
    solution: OptimizationSolution | None
    alternatives: tuple[OptimizationSolution, ...]
    objective_value: float | None
    solver_status: str
    decision_variables: dict[str, float | int | str]
    hard_constraints: tuple[str, ...]
    soft_constraints: tuple[str, ...]
    penalties: dict[str, float]
    explanation: str


__all__ = [
    "ConstraintStatus",
    "OptimizationOption",
    "OptimizationProblem",
    "OptimizationResult",
    "OptimizationSolution",
]
