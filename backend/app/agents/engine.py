"""Agent engine for processing chat with tools."""

import json
import logging
import re
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import TOOL_REGISTRY, BaseTool
from app.providers.llm import ChatMessage, llm_client
from app.services.agent_loader import agent_loader

logger = logging.getLogger(__name__)

# Pattern to match tool calls in LLM response
TOOL_CALL_PATTERN = re.compile(
    r'<tool>\s*(\{.*?\})\s*</tool>',
    re.DOTALL
)


@dataclass
class ToolCall:
    """Represents a tool call parsed from LLM response."""

    name: str
    params: dict[str, Any]


@dataclass
class AgentResponse:
    """Response from agent processing."""

    content: str
    tools_used: list[str] = field(default_factory=list)
    thinking: str | None = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    model: str | None = None
    usage: dict[str, int] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "tools_used": self.tools_used,
            "thinking": self.thinking,
            "sources": self.sources,
            "model": self.model,
            "usage": self.usage,
        }


class AgentEngine:
    """Engine for processing chat messages with agent capabilities."""

    def __init__(self, agent_slug: str) -> None:
        """Initialize agent engine.

        Args:
            agent_slug: Agent identifier to load configuration
        """
        self.agent_slug = agent_slug
        self.config = agent_loader.load_agent(agent_slug)

        if not self.config:
            raise ValueError(f"Agent not found: {agent_slug}")

        # Load tools for this agent
        self.tools: dict[str, BaseTool] = {}
        agent_tools = self.config.get("tools", [])
        for tool_name in agent_tools:
            if tool_name in TOOL_REGISTRY:
                self.tools[tool_name] = TOOL_REGISTRY[tool_name]
            else:
                logger.warning(f"Unknown tool '{tool_name}' for agent '{agent_slug}'")

        # Get settings
        self.settings = self.config.get("settings", {})
        self.temperature = self.settings.get("temperature", 0.7)
        self.max_tokens = self.settings.get("max_tokens", 4096)

    def _build_system_prompt(self) -> str:
        """Build system prompt with agent persona and tools description.

        Returns:
            Complete system prompt
        """
        # Get base persona prompt
        persona_prompt = agent_loader.get_system_prompt(self.agent_slug) or ""

        # Add tools description if any tools are available
        if self.tools:
            tools_desc = "\n\nYou have access to the following tools:\n"
            for name, tool in self.tools.items():
                tools_desc += f"\n- {name}: {tool.description}"

            tools_desc += """

To use a tool, include it in your response like this:
<tool>{"name": "tool_name", "params": {"param1": "value1"}}</tool>

You can use multiple tools by including multiple <tool>...</tool> blocks.
After using tools, provide your final response based on the tool results.

If a tool returns an error, acknowledge it and try to help without that tool."""
            return persona_prompt + tools_desc

        return persona_prompt

    def _parse_tool_calls(self, response: str) -> list[ToolCall]:
        """Parse tool calls from LLM response.

        Args:
            response: LLM response text

        Returns:
            List of parsed tool calls
        """
        tool_calls = []
        matches = TOOL_CALL_PATTERN.findall(response)

        for match in matches:
            try:
                data = json.loads(match)
                if "name" in data:
                    tool_calls.append(ToolCall(
                        name=data["name"],
                        params=data.get("params", {}),
                    ))
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse tool call: {match}, error: {e}")

        return tool_calls

    def _remove_tool_calls(self, response: str) -> str:
        """Remove tool call blocks from response.

        Args:
            response: LLM response with tool calls

        Returns:
            Response without tool call blocks
        """
        return TOOL_CALL_PATTERN.sub("", response).strip()

    async def _execute_tool(
        self,
        tool_call: ToolCall,
        db: AsyncSession | None = None,
        user_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a single tool call.

        Args:
            tool_call: Tool call to execute
            db: Database session (for tools that need it)
            user_id: User ID (for tools that need it)
            **kwargs: Additional tool parameters

        Returns:
            Tool result as dict
        """
        tool = self.tools.get(tool_call.name)
        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_call.name}",
            }

        try:
            # Merge params with context
            params = {**tool_call.params}
            if db is not None:
                params["db"] = db
            if user_id is not None:
                params["user_id"] = user_id
            params.update(kwargs)

            result = await tool.execute(**params)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Tool execution error: {tool_call.name}, {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def process(
        self,
        messages: list[ChatMessage],
        db: AsyncSession | None = None,
        user_id: uuid.UUID | None = None,
        max_iterations: int = 3,
        **kwargs: Any,
    ) -> AgentResponse:
        """Process messages with agent (non-streaming).

        Args:
            messages: Chat messages
            db: Database session for tool execution
            user_id: User ID for tool execution
            max_iterations: Maximum tool calling iterations
            **kwargs: Additional parameters

        Returns:
            AgentResponse with content and metadata
        """
        # Build messages with system prompt
        system_prompt = self._build_system_prompt()
        all_messages = [ChatMessage(role="system", content=system_prompt)] + messages

        tools_used = []
        sources = []
        thinking_parts = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        model_used = None

        for iteration in range(max_iterations):
            # Call LLM
            response = await llm_client.chat_completion(
                messages=all_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            model_used = response.model
            if response.usage:
                total_usage["prompt_tokens"] += response.usage.get("prompt_tokens", 0)
                total_usage["completion_tokens"] += response.usage.get("completion_tokens", 0)
                total_usage["total_tokens"] += response.usage.get("total_tokens", 0)

            # Parse tool calls
            tool_calls = self._parse_tool_calls(response.content)

            if not tool_calls:
                # No tool calls, return final response
                final_content = self._remove_tool_calls(response.content)
                return AgentResponse(
                    content=final_content,
                    tools_used=tools_used,
                    thinking="\n".join(thinking_parts) if thinking_parts else None,
                    sources=sources,
                    model=model_used,
                    usage=total_usage if total_usage["total_tokens"] > 0 else None,
                )

            # Execute tools and collect results
            tool_results = []
            for tool_call in tool_calls:
                tools_used.append(tool_call.name)
                thinking_parts.append(f"Using tool: {tool_call.name}")

                result = await self._execute_tool(
                    tool_call=tool_call,
                    db=db,
                    user_id=user_id,
                    **kwargs,
                )
                tool_results.append({
                    "tool": tool_call.name,
                    "result": result,
                })

                # Collect sources from RAG search results
                if tool_call.name == "rag_search" and result.get("success"):
                    for chunk in result.get("data", []):
                        sources.append(chunk)

            # Add assistant message and tool results to conversation
            all_messages.append(ChatMessage(role="assistant", content=response.content))
            all_messages.append(ChatMessage(
                role="user",
                content=f"Tool results:\n{json.dumps(tool_results, indent=2)}\n\nPlease provide your response based on these results.",
            ))

        # Max iterations reached
        return AgentResponse(
            content="I've reached my processing limit. Please try simplifying your request.",
            tools_used=tools_used,
            thinking="\n".join(thinking_parts) if thinking_parts else None,
            sources=sources,
            model=model_used,
            usage=total_usage if total_usage["total_tokens"] > 0 else None,
        )

    async def process_stream(
        self,
        messages: list[ChatMessage],
        db: AsyncSession | None = None,
        user_id: uuid.UUID | None = None,
        max_iterations: int = 3,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Process messages with agent (streaming).

        Yields events in the format:
        - {"type": "thinking", "content": "..."}
        - {"type": "tool_call", "name": "...", "params": {...}}
        - {"type": "tool_result", "name": "...", "result": {...}}
        - {"type": "content", "content": "...", "done": false}
        - {"type": "done", "tools_used": [...], "sources": [...]}

        Args:
            messages: Chat messages
            db: Database session for tool execution
            user_id: User ID for tool execution
            max_iterations: Maximum tool calling iterations
            **kwargs: Additional parameters

        Yields:
            Event dicts for streaming
        """
        # Build messages with system prompt
        system_prompt = self._build_system_prompt()
        all_messages = [ChatMessage(role="system", content=system_prompt)] + messages

        tools_used = []
        sources = []

        for iteration in range(max_iterations):
            # First, get a non-streaming response to check for tool calls
            response = await llm_client.chat_completion(
                messages=all_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Parse tool calls
            tool_calls = self._parse_tool_calls(response.content)

            if not tool_calls:
                # No tool calls, stream the final response
                async for chunk in llm_client.chat_completion_stream(
                    messages=all_messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                ):
                    yield {"type": "content", "content": chunk, "done": False}

                # Send done event
                yield {
                    "type": "done",
                    "tools_used": tools_used,
                    "sources": sources,
                }
                return

            # Show thinking
            yield {"type": "thinking", "content": f"Processing with {len(tool_calls)} tool(s)..."}

            # Execute tools
            tool_results = []
            for tool_call in tool_calls:
                tools_used.append(tool_call.name)

                yield {
                    "type": "tool_call",
                    "name": tool_call.name,
                    "params": tool_call.params,
                }

                result = await self._execute_tool(
                    tool_call=tool_call,
                    db=db,
                    user_id=user_id,
                    **kwargs,
                )

                yield {
                    "type": "tool_result",
                    "name": tool_call.name,
                    "result": result,
                }

                tool_results.append({
                    "tool": tool_call.name,
                    "result": result,
                })

                # Collect sources
                if tool_call.name == "rag_search" and result.get("success"):
                    for chunk in result.get("data", []):
                        sources.append(chunk)

            # Add to conversation for next iteration
            all_messages.append(ChatMessage(role="assistant", content=response.content))
            all_messages.append(ChatMessage(
                role="user",
                content=f"Tool results:\n{json.dumps(tool_results, indent=2)}\n\nPlease provide your response based on these results.",
            ))

        # Max iterations reached
        yield {
            "type": "content",
            "content": "I've reached my processing limit. Please try simplifying your request.",
            "done": True,
        }
        yield {
            "type": "done",
            "tools_used": tools_used,
            "sources": sources,
        }
