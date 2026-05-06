"""Quickstart MCP: mock MCP tool wrapper that emits a JEP event."""

import _bootstrap

from typing import Any

from jep_quickstart import create_event


def mcp_tool_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"content": f"mock MCP response from {tool_name}", "arguments": arguments}


def call_mcp_with_jep(tool_name: str, arguments: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    response = mcp_tool_call(tool_name, arguments)
    event = create_event("mcp.tool.call", tool_name, arguments, response, actor="mcp-server")
    return response, event.to_dict()


if __name__ == "__main__":
    response, event = call_mcp_with_jep("mock.get_weather", {"city": "Berlin"})
    print("mcp response:", response)
    print("jep event:", event)
