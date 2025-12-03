"""Agent API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.context import get_context
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.base import BaseResponse
from app.services.agent_loader import agent_loader

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentInfo(BaseModel):
    """Agent information response."""

    name: str
    slug: str
    icon: str | None = None
    description: str | None = None
    tools: list[str] = []
    settings: dict | None = None
    privacy: dict | None = None


class AgentDetailResponse(BaseModel):
    """Detailed agent response."""

    name: str
    slug: str
    icon: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    tools: list[str] = []
    settings: dict | None = None
    privacy: dict | None = None


class ToolInfo(BaseModel):
    """Tool information response."""

    name: str
    description: str


class AgentToolsResponse(BaseModel):
    """Agent tools response."""

    agent_slug: str
    tools: list[ToolInfo]


class AgentListResponse(BaseModel):
    """Agent list response."""

    agents: list[AgentInfo]
    total: int


@router.get("")
async def list_agents(
    current_user: User = Depends(get_current_user),
) -> BaseResponse[AgentListResponse]:
    """List all available agents."""
    ctx = get_context()

    agents_data = agent_loader.list_agents()

    agents = [
        AgentInfo(
            name=agent.get("name", ""),
            slug=agent.get("slug", ""),
            icon=agent.get("icon"),
            description=agent.get("description"),
            tools=agent.get("tools", []),
            settings=agent.get("settings"),
            privacy=agent.get("privacy"),
        )
        for agent in agents_data
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentListResponse(agents=agents, total=len(agents)),
    )


@router.get("/{slug}")
async def get_agent(
    slug: str,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[AgentDetailResponse]:
    """Get agent details by slug."""
    ctx = get_context()

    config = agent_loader.load_agent(slug)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {slug}")

    agent_info = config.get("agent", {})
    persona = config.get("persona", {})

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentDetailResponse(
            name=agent_info.get("name", ""),
            slug=agent_info.get("slug", slug),
            icon=agent_info.get("icon"),
            description=agent_info.get("description"),
            system_prompt=persona.get("system_prompt"),
            tools=config.get("tools", []),
            settings=config.get("settings"),
            privacy=config.get("privacy"),
        ),
    )


@router.get("/{slug}/tools")
async def get_agent_tools(
    slug: str,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[AgentToolsResponse]:
    """Get tools available for an agent."""
    ctx = get_context()

    config = agent_loader.load_agent(slug)
    if not config:
        raise HTTPException(status_code=404, detail=f"Agent not found: {slug}")

    # Import tool registry to get descriptions
    from app.agents.tools import TOOL_REGISTRY

    agent_tools = config.get("tools", [])
    tools = []

    for tool_name in agent_tools:
        tool = TOOL_REGISTRY.get(tool_name)
        if tool:
            tools.append(ToolInfo(
                name=tool_name,
                description=tool.description,
            ))
        else:
            tools.append(ToolInfo(
                name=tool_name,
                description="Tool not available",
            ))

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AgentToolsResponse(agent_slug=slug, tools=tools),
    )
