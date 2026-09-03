"""Approved tool registry adapter."""

from collections.abc import Callable

from app.copilot.models import ToolCall, ToolResponse
from app.copilot.registry import copilot_registry

ToolCaller = Callable[[ToolCall], ToolResponse]


def approved_tool_caller(call: ToolCall) -> ToolResponse:
    return copilot_registry.call(call)


__all__ = ["ToolCaller", "approved_tool_caller"]
