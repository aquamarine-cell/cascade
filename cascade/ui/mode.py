"""Mode cycling system: design -> plan -> build -> test."""

from dataclasses import dataclass
from typing import Optional

from .theme import DEFAULT_THEME, ProviderTheme

MODE_ORDER = ("design", "plan", "build", "test")

# Mode -> default provider mapping
_MODE_PROVIDER = {
    "design": "gemini",
    "plan": "claude",
    "build": "openai",
    "test": "openrouter",
}


@dataclass(frozen=True)
class ModeState:
    """Immutable mode state with cycling and provider override."""

    index: int = 0
    override_provider: Optional[str] = None

    @property
    def mode_name(self) -> str:
        return MODE_ORDER[self.index % len(MODE_ORDER)]

    @property
    def default_provider(self) -> str:
        return _MODE_PROVIDER[self.mode_name]

    @property
    def active_provider(self) -> str:
        return self.override_provider or self.default_provider

    @property
    def theme(self) -> ProviderTheme:
        return DEFAULT_THEME.get_provider(self.active_provider)

    def cycle(self) -> "ModeState":
        """Return a new ModeState advanced to the next mode."""
        return ModeState(
            index=(self.index + 1) % len(MODE_ORDER),
            override_provider=self.override_provider,
        )

    def with_override(self, provider: Optional[str]) -> "ModeState":
        """Return a new ModeState with a provider override (or None to reset)."""
        return ModeState(index=self.index, override_provider=provider)

    def format_indicator(self) -> str:
        """Format the mode indicator for display: e.g. 'plan . cla'."""
        abbr = self.theme.abbreviation
        return f"{self.mode_name} . {abbr}"
