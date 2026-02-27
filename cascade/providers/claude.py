"""Anthropic Claude provider implementation."""

from typing import Optional, Iterator
import json
import httpx
from .base import BaseProvider, ProviderConfig


class ClaudeProvider(BaseProvider):
    """Anthropic Claude API provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://api.anthropic.com/v1"
        self.client = httpx.Client(timeout=60.0)

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Get a complete response from Claude."""
        return "".join(self.stream(prompt, system))

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        """Stream tokens from Claude."""
        try:
            url = f"{self.base_url}/messages"
            headers = {
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            
            payload = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens or 2048,
                "temperature": self.config.temperature,
                "stream": True,
                "messages": [{"role": "user", "content": prompt}],
            }
            
            if system:
                payload["system"] = system
            
            with self.client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            if data.get("type") == "content_block_delta":
                                if "delta" in data and "text" in data["delta"]:
                                    yield data["delta"]["text"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"Error: {str(e)}"

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
        except:
            pass
