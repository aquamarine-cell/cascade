"""Response metadata from provider API calls."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderResponse:
    """Immutable container for provider response with usage metadata.

    Wraps the text response along with token counts, model info,
    and latency from the API call.
    """

    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    latency_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def format_tokens(self) -> str:
        """Human-readable token summary."""
        def _fmt(n: int) -> str:
            if n >= 1000:
                return f"~{n / 1000:.1f}k"
            return f"~{n}"
        return f"{_fmt(self.input_tokens)} in / {_fmt(self.output_tokens)} out"
