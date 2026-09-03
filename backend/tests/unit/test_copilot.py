from app.copilot.models import CopilotSession, ToolCall
from app.copilot.registry import copilot_registry


def _call(tool: str, artifacts: dict, **arguments):
    return ToolCall(
        tool=tool,
        arguments=arguments,
        session=CopilotSession(
            session_id="session-1",
            source_state_snapshot="snapshot-1",
            artifacts=artifacts,
        ),
    )


def test_registered_tool_returns_authoritative_artifact_and_context() -> None:
    response = copilot_registry.call(
        _call("get_freight_forecast", {"get_freight_forecast": {"p50": 42}})
    )

    assert response.ok
    assert response.data == {"p50": 42}
    assert response.source_state_snapshot == "snapshot-1"
    assert response.source == "navisail.engine.get_freight_forecast"
    assert len(copilot_registry.list_tools()) == 13


def test_missing_artifact_and_transaction_request_are_safe_errors() -> None:
    missing = copilot_registry.call(_call("get_recommendation", {}))
    denied = copilot_registry.call(
        _call(
            "get_recommendation",
            {"get_recommendation": {"decision": "Recommended"}},
            query="approve and execute the booking",
        )
    )

    assert missing.ok is False
    assert missing.error_code == "artifact_unavailable"
    assert denied.ok is False
    assert denied.error_code == "policy_denied"
