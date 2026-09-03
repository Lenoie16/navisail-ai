from time import sleep

from app.copilot.models import ToolResponse
from app.dynamic_agents.factory import create_agent
from app.dynamic_agents.shared.models import AgentBudget, AgentRequest


def _request(question: str, **budget) -> AgentRequest:
    return AgentRequest(
        session_id="s-1",
        question=question,
        source_state_snapshot="snapshot-1",
        budget=AgentBudget(**budget),
        context={"artifacts": {"get_freight_forecast": {"p50": 42}}},
    )


def test_normal_flow_uses_approved_tool_and_emits_events() -> None:
    result = create_agent().run(_request("What is the freight forecast?"))
    assert result.status == "completed"
    assert result.tool_results == {"get_freight_forecast": {"p50": 42}}
    assert any(event.type.value == "tool_completed" for event in result.events)


def test_tool_error_is_bounded() -> None:
    def failing(call):
        return ToolResponse(
            ok=False,
            tool=call.tool,
            session_id=call.session.session_id,
            source="test",
            source_state_snapshot="snapshot-1",
            error_code="failed",
            error_message="synthetic tool failure",
        )

    result = create_agent(failing).run(_request("What is the freight forecast?"))
    assert result.status == "failed"
    assert "synthetic tool failure" in result.answer


def test_missing_capability_and_budget_exhaustion() -> None:
    missing = create_agent().run(_request("Tell me an unrelated story"))
    exhausted = create_agent().run(_request("Compare freight and congestion", max_tool_calls=1))
    assert missing.missing_capabilities
    assert exhausted.status == "failed"
    assert exhausted.answer == "tool-call budget exhausted"


def test_timeout_and_reflection_termination() -> None:
    def slow(call):
        sleep(0.02)
        return ToolResponse(
            ok=True,
            tool=call.tool,
            session_id=call.session.session_id,
            source="test",
            source_state_snapshot="snapshot-1",
            data={"ok": True},
        )

    timeout = create_agent(slow).run(
        _request("What is the freight forecast?", timeout_seconds=0.001)
    )
    assert timeout.answer == "agent timeout"

    reflection = create_agent().run(
        _request("What is the freight forecast?", max_reflection_loops=0)
    )
    assert reflection.reflection_loops == 0
