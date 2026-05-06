"""Quickstart OpenAI Agents: pseudo middleware around a tool call."""

import _bootstrap

from typing import Any, Callable

from jep_quickstart import create_event


def jep_tool_middleware(tool_name: str, tool: Callable[..., Any]) -> Callable[..., tuple[Any, dict[str, Any]]]:
    def call(**kwargs: Any) -> tuple[Any, dict[str, Any]]:
        result = tool(**kwargs)
        event = create_event("openai_agents.tool.call", tool_name, kwargs, result, actor="openai-agent")
        return result, event.to_dict()

    return call


def mock_lookup(order_id: str) -> dict[str, str]:
    return {"order_id": order_id, "status": "shipped"}


if __name__ == "__main__":
    lookup = jep_tool_middleware("mock_lookup", mock_lookup)
    result, event = lookup(order_id="A-100")
    print("tool result:", result)
    print("jep event:", event)
