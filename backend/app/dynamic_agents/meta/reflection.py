"""Bounded reflection that identifies evidence gaps only."""

from app.dynamic_agents.shared.models import AgentPlan


def reflect(plan: AgentPlan, results: dict[str, object]) -> tuple[str, ...]:
    missing = list(plan.missing_capabilities)
    missing.extend(
        f"evidence for {tool}" for tool in plan.tools if tool not in results
    )
    return tuple(dict.fromkeys(missing))


__all__ = ["reflect"]
