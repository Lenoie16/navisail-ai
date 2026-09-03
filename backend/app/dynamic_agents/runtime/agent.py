"""Bounded orchestration runtime."""

from __future__ import annotations

from time import monotonic

from app.copilot.models import CopilotSession, ToolCall
from app.dynamic_agents.graph.planner import plan_question
from app.dynamic_agents.meta.reflection import reflect
from app.dynamic_agents.registry.tools import ToolCaller, approved_tool_caller
from app.dynamic_agents.shared.models import (
    AgentEvent,
    AgentEventType,
    AgentRequest,
    AgentRunResult,
)


class DynamicAgent:
    def __init__(self, tool_caller: ToolCaller = approved_tool_caller) -> None:
        self.tool_caller = tool_caller

    def run(self, request: AgentRequest) -> AgentRunResult:
        started = monotonic()
        agent_id = f"agent-{request.session_id}"
        events: list[AgentEvent] = [
            AgentEvent(
                type=AgentEventType.STARTED,
                agent_id=agent_id,
                session_id=request.session_id,
                message="Bounded agent started.",
            )
        ]
        plan = plan_question(request.question)
        events.append(
            AgentEvent(
                type=AgentEventType.PLAN_CREATED,
                agent_id=agent_id,
                session_id=request.session_id,
                message=plan.rationale,
                metadata={"tools": plan.tools},
            )
        )
        if request.budget.max_agents < 1:
            return self._failed(request, agent_id, events, "agent budget exhausted")
        if plan.missing_capabilities:
            return self._failed(
                request,
                agent_id,
                events,
                "missing approved capability",
                missing=plan.missing_capabilities,
            )
        session = CopilotSession(
            session_id=request.session_id,
            source_state_snapshot=request.source_state_snapshot,
            artifacts=request.context.get("artifacts", {}),
        )
        results: dict[str, object] = {}
        for index, tool in enumerate(plan.tools):
            if index >= request.budget.max_tool_calls:
                return self._failed(request, agent_id, events, "tool-call budget exhausted")
            if monotonic() - started > request.budget.timeout_seconds:
                return self._failed(request, agent_id, events, "agent timeout")
            events.append(
                AgentEvent(
                    type=AgentEventType.TOOL_STARTED,
                    agent_id=agent_id,
                    session_id=request.session_id,
                    message=f"Calling approved tool {tool}.",
                    tool=tool,
                )
            )
            response = self.tool_caller(
                ToolCall(tool=tool, arguments={}, session=session)
            )
            if monotonic() - started > request.budget.timeout_seconds:
                return self._failed(request, agent_id, events, "agent timeout")
            if not response.ok:
                events.append(
                    AgentEvent(
                        type=AgentEventType.TOOL_FAILED,
                        agent_id=agent_id,
                        session_id=request.session_id,
                        message=response.error_message or "Tool failed.",
                        tool=tool,
                    )
                )
                return self._failed(
                    request, agent_id, events, response.error_message or "tool error"
                )
            results[tool] = response.data
            events.append(
                AgentEvent(
                    type=AgentEventType.TOOL_COMPLETED,
                    agent_id=agent_id,
                    session_id=request.session_id,
                    message=f"Tool {tool} completed.",
                    tool=tool,
                )
            )
        reflection_loops = 0
        gaps = reflect(plan, results)
        while gaps and reflection_loops < request.budget.max_reflection_loops:
            reflection_loops += 1
            events.append(
                AgentEvent(
                    type=AgentEventType.REFLECTION,
                    agent_id=agent_id,
                    session_id=request.session_id,
                    message=(
                        "Reflection identified evidence gaps; no numerical inference "
                        "performed."
                    ),
                    metadata={"missing": gaps, "loop": reflection_loops},
                )
            )
            gaps = ()
        status = "completed" if not gaps else "reflection_terminated"
        events.append(
            AgentEvent(
                type=AgentEventType.COMPLETED,
                agent_id=agent_id,
                session_id=request.session_id,
                message="Agent completed using approved tool outputs.",
            )
        )
        return AgentRunResult(
            status=status,
            agent_id=agent_id,
            session_id=request.session_id,
            answer=" ".join(f"{tool}: authoritative result available." for tool in results),
            tool_results=results,
            events=tuple(events),
            reflection_loops=reflection_loops,
            tool_calls=len(results),
            source_state_snapshot=request.source_state_snapshot,
        )

    @staticmethod
    def _failed(
        request: AgentRequest,
        agent_id: str,
        events: list[AgentEvent],
        message: str,
        *,
        missing: tuple[str, ...] = (),
    ) -> AgentRunResult:
        events.append(
            AgentEvent(
                type=AgentEventType.FAILED,
                agent_id=agent_id,
                session_id=request.session_id,
                message=message,
            )
        )
        return AgentRunResult(
            status="failed",
            agent_id=agent_id,
            session_id=request.session_id,
            answer=message,
            missing_capabilities=missing,
            events=tuple(events),
            source_state_snapshot=request.source_state_snapshot,
        )


__all__ = ["DynamicAgent"]
