"""OpenAI provider for GPT-4o, o1, o3, and Codex models."""

import json
from typing import Optional, Iterator, TYPE_CHECKING
import httpx
from .base import BaseProvider, ProviderConfig
from .registry import register_provider
from ._openai_tools import openai_ask_with_tools

if TYPE_CHECKING:
    from ..tools.schema import ToolDef


@register_provider("openai")
class OpenAIProvider(BaseProvider):
    """OpenAI API provider - supports custom base_url for Azure/proxies."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.client = httpx.Client(timeout=60.0)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Get a complete response from OpenAI."""
        return "".join(self.stream(prompt, system))

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        """Stream tokens from OpenAI."""
        self._last_usage = None
        try:
            url = f"{self.base_url}/chat/completions"

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": True,
                "stream_options": {"include_usage": True},
                "temperature": self.config.temperature,
            }
            if self.config.max_tokens:
                payload["max_tokens"] = self.config.max_tokens

            with self.client.stream("POST", url, json=payload, headers=self._headers()) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        usage = data.get("usage")
                        if usage:
                            self._last_usage = (
                                usage.get("prompt_tokens", 0),
                                usage.get("completion_tokens", 0),
                            )
                        choices = data.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
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
        """OpenAI-native tool calling."""
        return openai_ask_with_tools(
            client=self.client,
            url=f"{self.base_url}/chat/completions",
            headers=self._headers(),
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            prompt=prompt,
            tools=tools,
            system=system,
            max_rounds=max_rounds,
        )

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
