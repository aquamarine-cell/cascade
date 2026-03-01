"""Anthropic Claude provider implementation."""

from typing import Optional, Iterator, TYPE_CHECKING
import json
import httpx
from .base import BaseProvider, ProviderConfig
from .registry import register_provider

if TYPE_CHECKING:
    from ..tools.schema import ToolDef


@register_provider("claude")
class ClaudeProvider(BaseProvider):
    """Anthropic Claude API provider.

    Supports both standard API keys and OAuth tokens from Claude Code CLI.
    OAuth tokens (``sk-ant-oat01-`` prefix) use the same ``x-api-key``
    header as regular keys.
    """

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
        self.client = httpx.Client(timeout=60.0)

    def _headers(self) -> dict:
        return {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Get a complete response from Claude."""
        return "".join(self.stream(prompt, system))

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        """Stream tokens from Claude."""
        self._last_usage = None
        try:
            url = f"{self.base_url}/messages"
            payload = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens or 2048,
                "temperature": self.config.temperature,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system:
                payload["system"] = system

            with self.client.stream("POST", url, json=payload, headers=self._headers()) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data.get("type") == "content_block_delta":
                                if "delta" in data and "text" in data["delta"]:
                                    yield data["delta"]["text"]
                            elif data.get("type") == "message_delta":
                                usage = data.get("usage", {})
                                out_tokens = usage.get("output_tokens", 0)
                                if out_tokens:
                                    prev = self._last_usage or (0, 0)
                                    self._last_usage = (prev[0], out_tokens)
                            elif data.get("type") == "message_start":
                                usage = data.get("message", {}).get("usage", {})
                                in_tokens = usage.get("input_tokens", 0)
                                self._last_usage = (in_tokens, 0)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"Error: {str(e)}"

    def ask_with_tools(
        self,
        prompt: str,
        tools: dict[str, "ToolDef"],
        system: Optional[str] = None,
        max_rounds: int = 5,
    ) -> tuple[str, list[dict]]:
        """Claude-native tool calling using tools array + tool_use/tool_result."""
        from ..tools.executor import ToolExecutor

        executor = ToolExecutor(tools)
        tool_defs = [
            {
                "name": td.name,
                "description": td.description,
                "input_schema": td.parameters,
            }
            for td in tools.values()
        ]

        messages = [{"role": "user", "content": prompt}]
        tool_log = []

        for _ in range(max_rounds):
            payload = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens or 2048,
                "temperature": self.config.temperature,
                "messages": messages,
                "tools": tool_defs,
            }
            if system:
                payload["system"] = system

            url = f"{self.base_url}/messages"
            try:
                response = self.client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error: {e}", tool_log

            # Capture token usage
            usage = data.get("usage", {})
            in_t = usage.get("input_tokens", 0)
            out_t = usage.get("output_tokens", 0)
            if in_t or out_t:
                prev = self._last_usage or (0, 0)
                self._last_usage = (prev[0] + in_t, prev[1] + out_t)

            # Check stop reason
            stop_reason = data.get("stop_reason", "end_turn")

            # Extract text and tool_use blocks
            text_parts = []
            tool_uses = []
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_uses.append(block)

            if not tool_uses or stop_reason != "tool_use":
                return "".join(text_parts), tool_log

            # Append the assistant message with all content blocks
            messages.append({"role": "assistant", "content": data["content"]})

            # Execute each tool call and build tool_result messages
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use["name"]
                tool_input = tool_use.get("input", {})
                tool_id = tool_use["id"]

                result = executor.execute(tool_name, tool_input)
                tool_log.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "output": result,
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

        # Exhausted rounds, return whatever text we have
        return "".join(text_parts) if text_parts else "", tool_log

    def compare(self, prompt: str, system: Optional[str] = None) -> dict:
        """Generate comparison data."""
        response = self.ask(prompt, system)
        return {
            "provider": self.name,
            "model": self.config.model,
            "response": response,
            "length": len(response),
        }

    def __del__(self):
        """Cleanup HTTP client."""
        try:
            self.client.close()
        except Exception:
            pass
