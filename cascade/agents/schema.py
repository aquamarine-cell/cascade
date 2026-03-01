"""Agent definition dataclass."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AgentDef:
    """Immutable definition of a named agent.

    Agents override provider/model/temperature/system_prompt for a single
    interaction.  ``allowed_tools`` controls which tools are available:

    * ``None``  -- unrestricted (all registered tools)
    * ``()``    -- no tools at all
    * ``("read_file", "write_file")`` -- only the listed tools
    """

    name: str
    description: str = ""
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_prompt: str = ""
    allowed_tools: Optional[tuple[str, ...]] = None
    max_tokens: Optional[int] = None

    def to_summary(self) -> str:
        """One-line human-readable summary for /agents listing."""
        parts = [self.name]
        if self.description:
            parts.append(f"- {self.description}")
        overrides = []
        if self.provider:
            overrides.append(f"provider={self.provider}")
        if self.model:
            overrides.append(f"model={self.model}")
        if self.allowed_tools is not None:
            overrides.append(f"tools={len(self.allowed_tools)}")
        if overrides:
            parts.append(f"[{', '.join(overrides)}]")
        return "  ".join(parts)
