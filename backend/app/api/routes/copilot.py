"""Controlled copilot tool endpoint."""

from fastapi import APIRouter

from app.copilot.models import ToolCall, ToolResponse
from app.copilot.registry import copilot_registry
from app.dynamic_agents.factory import create_agent
from app.dynamic_agents.shared.models import AgentRequest, AgentRunResult

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.get("/tools")
async def list_copilot_tools() -> list[dict[str, str]]:
    return [
        {
            "name": definition.name,
            "description": definition.description,
            "output_description": definition.output_description,
        }
        for definition in copilot_registry.list_tools()
    ]


@router.post("/tools/call", response_model=ToolResponse)
async def call_copilot_tool(request: ToolCall) -> ToolResponse:
    return copilot_registry.call(request)


@router.post("/agent/run", response_model=AgentRunResult)
async def run_dynamic_agent(request: AgentRequest) -> AgentRunResult:
    return create_agent().run(request)
