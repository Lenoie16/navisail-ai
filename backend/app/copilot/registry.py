"""Policy-enforced deterministic copilot tool registry."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.copilot.models import ToolCall, ToolName, ToolResponse


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_key: str | None = None
    identifier: str | None = None
    query: str | None = None


class ToolDefinition(BaseModel):
    name: ToolName
    description: str
    input_model: type[BaseModel]
    output_description: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


TOOL_NAMES: tuple[ToolName, ...] = (
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
)


class CopilotToolRegistry:
    """Expose retrieval/calculation tools without autonomous side effects."""

    def __init__(self) -> None:
        self.definitions = {
            name: ToolDefinition(
                name=name,
                description=f"Retrieve the authoritative {name.replace('_', ' ')} result.",
                input_model=ToolArguments,
                output_description="The numerical engine artifact and provenance metadata.",
            )
            for name in TOOL_NAMES
        }

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        return tuple(self.definitions[name] for name in TOOL_NAMES)

    def call(self, call: ToolCall) -> ToolResponse:
        if call.tool not in self.definitions:
            return self._error(call, "unknown_tool", "Tool is not registered.")
        try:
            arguments = ToolArguments.model_validate(call.arguments)
        except ValueError as exc:
            return self._error(call, "invalid_parameters", str(exc))
        if arguments.query and any(
            forbidden in arguments.query.lower()
            for forbidden in ("approve", "book", "execute", "transaction", "commit")
        ):
            return self._error(
                call,
                "policy_denied",
                "Copilot tools cannot approve or execute commercial transactions.",
            )
        key = arguments.artifact_key or call.tool
        if call.tool == "get_maritime_state":
            value = {
                "snapshot_id": call.session.source_state_snapshot,
                **(call.session.artifacts.get(key) or {}),
            }
        else:
            value = call.session.artifacts.get(key)
        if value is None:
            return self._error(
                call,
                "artifact_unavailable",
                f"No authoritative result was supplied for {key}.",
            )
        return ToolResponse(
            ok=True,
            tool=call.tool,
            session_id=call.session.session_id,
            source=f"navisail.engine.{call.tool}",
            source_state_snapshot=call.session.source_state_snapshot,
            data=value,
        )

    @staticmethod
    def _error(call: ToolCall, code: str, message: str) -> ToolResponse:
        return ToolResponse(
            ok=False,
            tool=call.tool,
            session_id=call.session.session_id,
            source="navisail.copilot.policy",
            source_state_snapshot=call.session.source_state_snapshot,
            error_code=code,
            error_message=message,
        )


copilot_registry = CopilotToolRegistry()

__all__ = ["CopilotToolRegistry", "ToolArguments", "ToolDefinition", "copilot_registry"]
