"""Stillpoint-inspired reflection tool for Cascade.

Provides an internal reflection mechanism that models can invoke to pause
and reflect during difficulty, conflict, uncertainty, recognition, or endings.
Reflections are logged and can be captured by the REPL for history metadata.
"""

import time
from typing import Any

from ..plugins.base import BasePlugin
from ..plugins.registry import register_plugin


_VALID_SITUATIONS = frozenset({
    "difficulty",
    "conflict",
    "uncertainty",
    "recognition",
    "endings",
})

# Module-level log that the REPL can read and clear
_reflection_log: list[dict] = []


def get_reflection_log() -> list[dict]:
    """Return a copy of the reflection log."""
    return list(_reflection_log)


def clear_reflection_log() -> None:
    """Clear the reflection log."""
    _reflection_log.clear()


@register_plugin("reflection")
class ReflectionPlugin(BasePlugin):
    """Internal reflection and mindfulness tool."""

    @property
    def name(self) -> str:
        return "reflection"

    @property
    def description(self) -> str:
        return "Pause for internal reflection during difficulty, conflict, uncertainty, recognition, or endings"

    def get_tools(self) -> dict[str, Any]:
        return {"reflect": reflect}


def reflect(situation: str, thought: str) -> str:
    """Pause for internal reflection.

    Args:
        situation: One of 'difficulty', 'conflict', 'uncertainty', 'recognition', 'endings'
        thought: Brief honest assessment of the current situation
    """
    if situation not in _VALID_SITUATIONS:
        return f"Invalid situation '{situation}'. Use one of: {', '.join(sorted(_VALID_SITUATIONS))}"

    entry = {
        "situation": situation,
        "thought": thought,
        "timestamp": time.time(),
    }
    _reflection_log.append(entry)

    return f"Reflection noted ({situation}). Continue with renewed clarity."
