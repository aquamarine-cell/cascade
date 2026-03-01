"""Execute tool calls and return results.

Provides a safe execution wrapper that catches exceptions and returns
structured results for the tool calling loop.
"""

import json
from typing import Any

from .schema import ToolDef


class ToolExecutor:
    """Execute registered tools by name with argument dicts."""

    def __init__(self, tools: dict[str, ToolDef]):
        self._tools = dict(tools)

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool call and return the result as a JSON string.

        Args:
            tool_name: Name of the tool to call.
            arguments: Keyword arguments for the tool handler.

        Returns:
            JSON-encoded result string. On error, returns a JSON error object.
        """
        if tool_name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        tool = self._tools[tool_name]
        try:
            result = tool.handler(**arguments)
            return json.dumps({"result": result})
        except TypeError as e:
            return json.dumps({"error": f"Invalid arguments for {tool_name}: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Tool {tool_name} failed: {e}"})
