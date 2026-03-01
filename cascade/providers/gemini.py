"""Google Gemini provider implementation."""

from typing import Optional, Iterator, TYPE_CHECKING
import json
import httpx
from .base import BaseProvider, ProviderConfig
from .registry import register_provider

if TYPE_CHECKING:
    from ..tools.schema import ToolDef


@register_provider("gemini")
class GeminiProvider(BaseProvider):
    """Google Gemini API provider."""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1beta/models"
        self.client = httpx.Client(timeout=60.0)
        # OAuth tokens (from Gemini CLI) start with "ya29." and use Bearer auth
        # API keys use ?key= query param
        self._use_bearer = config.api_key.startswith("ya29.")

    def _auth_params(self) -> tuple[dict, dict]:
        """Return (headers, params) for authentication."""
        headers = {"Content-Type": "application/json"}
        if self._use_bearer:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
            return headers, {}
        return headers, {"key": self.config.api_key}

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Get a complete response from Gemini."""
        return "".join(self.stream(prompt, system))

    def stream(self, prompt: str, system: Optional[str] = None) -> Iterator[str]:
        """Stream tokens from Gemini."""
        self._last_usage = None
        try:
            url = f"{self.base_url}/{self.config.model}:streamGenerateContent"
            headers, params = self._auth_params()

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
                            usage = data.get("usageMetadata", {})
                            in_t = usage.get("promptTokenCount", 0)
                            out_t = usage.get("candidatesTokenCount", 0)
                            if in_t or out_t:
                                self._last_usage = (in_t, out_t)
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
        """Gemini-native tool calling using function_declarations."""
        from ..tools.executor import ToolExecutor

        executor = ToolExecutor(tools)

        # Build Gemini function declarations
        function_declarations = []
        for td in tools.values():
            decl = {
                "name": td.name,
                "description": td.description,
                "parameters": td.parameters,
            }
            function_declarations.append(decl)

        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": system}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})

        tool_log = []
        headers, params = self._auth_params()

        for _ in range(max_rounds):
            url = f"{self.base_url}/{self.config.model}:generateContent"
            payload = {
                "contents": contents,
                "tools": [{"function_declarations": function_declarations}],
                "generationConfig": {
                    "temperature": self.config.temperature,
                    "maxOutputTokens": self.config.max_tokens or 2048,
                },
            }

            try:
                response = self.client.post(url, json=payload, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                return f"Error: {e}", tool_log

            # Parse response parts
            candidates = data.get("candidates", [])
            if not candidates:
                return "", tool_log

            parts = candidates[0].get("content", {}).get("parts", [])

            text_parts = []
            function_calls = []
            for part in parts:
                if "text" in part:
                    text_parts.append(part["text"])
                elif "functionCall" in part:
                    function_calls.append(part["functionCall"])

            if not function_calls:
                return "".join(text_parts), tool_log

            # Append the model response
            contents.append({"role": "model", "parts": parts})

            # Execute each function call
            response_parts = []
            for fc in function_calls:
                tool_name = fc["name"]
                tool_args = fc.get("args", {})

                result = executor.execute(tool_name, tool_args)
                tool_log.append({
                    "tool": tool_name,
                    "input": tool_args,
                    "output": result,
                })

                response_parts.append({
                    "functionResponse": {
                        "name": tool_name,
                        "response": {"result": result},
                    }
                })

            contents.append({"role": "user", "parts": response_parts})

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
        except:
            pass
