"""Google Gemini provider implementation."""

from typing import Optional, Iterator
import json
import httpx
from .base import BaseProvider, ProviderConfig


class GeminiProvider(BaseProvider):
    """Google Gemini API provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.client = httpx.Client(timeout=60.0)

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Get a complete response from Gemini."""
        return "".join(self.stream(prompt, system))

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        """Stream tokens from Gemini."""
        try:
            # Build request
            url = f"{self.base_url}/{self.config.model}:streamGenerateContent"
            headers = {"Content-Type": "application/json"}
            
            contents = []
            if system:
                contents.append({"role": "user", "parts": [{"text": system}]})
                contents.append({"role": "model", "parts": [{"text": "Understood."}]})
            
            contents.append({"role": "user", "parts": [{"text": prompt}]})
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens or 2048,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_UNSPECIFIED",
                        "threshold": "BLOCK_NONE",
                    }
                ],
            }
            
            params = {"key": self.config.api_key}
            
            with self.client.stream("POST", url, json=payload, params=params, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "candidates" in data:
                                for candidate in data["candidates"]:
                                    if "content" in candidate:
                                        for part in candidate["content"].get("parts", []):
                                            if "text" in part:
                                                yield part["text"]
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
