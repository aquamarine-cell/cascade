"""Base plugin interface for extending Cascade."""

from abc import ABC, abstractmethod
from typing import Any


class BasePlugin(ABC):
    """Abstract base class for all Cascade plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this plugin does."""

    def configure(self, config: dict) -> None:
        """Apply per-agent or per-project configuration.

        Override in subclasses to accept plugin-specific settings.
        Default implementation is a no-op.
        """

    @abstractmethod
    def get_tools(self) -> dict[str, Any]:
        """Return a mapping of tool_name -> callable for this plugin.

        Each callable represents a tool the AI agent can invoke.
        """
