"""Factory for bounded runtime agents."""

from app.dynamic_agents.registry.tools import ToolCaller
from app.dynamic_agents.runtime.agent import DynamicAgent


def create_agent(tool_caller: ToolCaller | None = None) -> DynamicAgent:
    return DynamicAgent() if tool_caller is None else DynamicAgent(tool_caller=tool_caller)


__all__ = ["create_agent"]
