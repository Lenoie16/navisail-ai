"""Shared contracts for bounded dynamic agents."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentEventType(StrEnum):
    STARTED = "started"
    PLAN_CREATED = "plan_created"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    REFLECTION = "reflection"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: AgentEventType
    agent_id: str
    session_id: str
    message: str
    tool: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentBudget(BaseModel):
    max_agents: int = Field(default=3, ge=1)
    max_reflection_loops: int = Field(default=2, ge=0)
    max_tool_calls: int = Field(default=10, ge=1)
    timeout_seconds: float = Field(default=5, gt=0)


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    source_state_snapshot: str = Field(min_length=1)
    budget: AgentBudget = Field(default_factory=AgentBudget)
    context: dict[str, Any] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    tools: tuple[str, ...]
    missing_capabilities: tuple[str, ...] = ()
    rationale: str


class AgentRunResult(BaseModel):
    status: str
    agent_id: str
    session_id: str
    answer: str
    tool_results: dict[str, Any] = Field(default_factory=dict)
    missing_capabilities: tuple[str, ...] = ()
    events: tuple[AgentEvent, ...]
    reflection_loops: int = 0
    tool_calls: int = 0
    source_state_snapshot: str


__all__ = [
    "AgentBudget",
    "AgentEvent",
    "AgentEventType",
    "AgentPlan",
    "AgentRequest",
    "AgentRunResult",
]
