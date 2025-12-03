"""Agent tools module."""

from app.agents.tools.base import BaseTool, ToolResult
from app.agents.tools.calculator import calculator_tool
from app.agents.tools.rag_search import rag_search_tool
from app.agents.tools.summarize import summarize_tool

# Tool registry - maps tool names to instances
TOOL_REGISTRY: dict[str, BaseTool] = {
    "rag_search": rag_search_tool,
    "summarize": summarize_tool,
    "calculator": calculator_tool,
}


def get_tool(name: str) -> BaseTool | None:
    """Get a tool instance by name.

    Args:
        name: Tool name

    Returns:
        Tool instance or None if not found
    """
    return TOOL_REGISTRY.get(name)


def list_tools() -> list[str]:
    """Get list of available tool names.

    Returns:
        List of tool names
    """
    return list(TOOL_REGISTRY.keys())


__all__ = [
    "BaseTool",
    "ToolResult",
    "TOOL_REGISTRY",
    "get_tool",
    "list_tools",
    "rag_search_tool",
    "summarize_tool",
    "calculator_tool",
]
