"""OpenRouter provider for multi-model access (Qwen, etc)."""

import httpx
from typing import Optional, AsyncGenerator
from .base import BaseProvider


class OpenRouterProvider(BaseProvider):
    """Provider for OpenRouter API models (Qwen, etc)."""

    def __init__(self, config: dict):
        """Initialize OpenRouter provider.
        
        Args:
            config: Dict with 'api_key' and optional 'model' (default: qwen3.5-35b-a3b).
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "qwen/qwen3.5-35b-a3b")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

    async def query(self, prompt: str, **kwargs) -> str:
        """Send query to OpenRouter and get response.
        
        Args:
            prompt: User prompt/question.
            **kwargs: Additional parameters (temperature, max_tokens, etc).
        
        Returns:
            Response text from the model.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://cascade.ai",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response from OpenRouter.
        
        Args:
            prompt: User prompt/question.
            **kwargs: Additional parameters.
        
        Yields:
            Streamed response chunks.
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://cascade.ai",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 2048),
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            import json
                            data = json.loads(line[6:])
                            if "choices" in data and data["choices"]:
                                chunk = data["choices"][0].get("delta", {}).get("content", "")
                                if chunk:
                                    yield chunk
                        except (json.JSONDecodeError, KeyError):
                            continue
