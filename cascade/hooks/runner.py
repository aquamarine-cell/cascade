"""Hook runner for lifecycle events.

Executes shell commands at defined lifecycle points (before_ask, after_response,
on_exit, on_error) with CASCADE_* environment variables for context.
"""

import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class HookEvent(str, Enum):
    """Lifecycle events that can trigger hooks."""

    BEFORE_ASK = "before_ask"
    AFTER_RESPONSE = "after_response"
    ON_EXIT = "on_exit"
    ON_ERROR = "on_error"


@dataclass(frozen=True)
class HookDefinition:
    """A single hook configuration."""

    name: str
    event: HookEvent
    command: str
    timeout: int = 30
    enabled: bool = True


class HookRunner:
    """Execute hooks at lifecycle events."""

    def __init__(self, hooks: tuple[HookDefinition, ...] = ()):
        self._hooks = hooks

    @property
    def hook_count(self) -> int:
        return len(self._hooks)

    def hooks_for_event(self, event: HookEvent) -> tuple[HookDefinition, ...]:
        """Return all enabled hooks for a given event."""
        return tuple(
            h for h in self._hooks
            if h.event == event and h.enabled
        )

    def run_hooks(
        self,
        event: HookEvent,
        context: Optional[dict[str, Any]] = None,
    ) -> list[dict]:
        """Execute all enabled hooks for an event.

        Args:
            event: The lifecycle event that triggered.
            context: Key-value pairs to set as CASCADE_* environment variables.

        Returns:
            List of result dicts with keys: name, success, output, duration.
        """
        hooks = self.hooks_for_event(event)
        if not hooks:
            return []

        env = dict(os.environ)
        env["CASCADE_EVENT"] = event.value

        if context:
            for key, value in context.items():
                env_key = f"CASCADE_{key.upper()}"
                env[env_key] = str(value)

        results = []
        for hook in hooks:
            result = self._run_single(hook, env)
            results.append(result)

        return results

    def _run_single(self, hook: HookDefinition, env: dict) -> dict:
        """Execute a single hook command."""
        start = time.monotonic()
        try:
            proc = subprocess.run(
                hook.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=hook.timeout,
                env=env,
            )
            duration = time.monotonic() - start
            return {
                "name": hook.name,
                "success": proc.returncode == 0,
                "output": proc.stdout.strip() or proc.stderr.strip(),
                "return_code": proc.returncode,
                "duration": round(duration, 3),
            }
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            return {
                "name": hook.name,
                "success": False,
                "output": f"Hook timed out after {hook.timeout}s",
                "return_code": -1,
                "duration": round(duration, 3),
            }
        except Exception as e:
            duration = time.monotonic() - start
            return {
                "name": hook.name,
                "success": False,
                "output": f"Hook failed: {e}",
                "return_code": -1,
                "duration": round(duration, 3),
            }

    def describe(self) -> list[dict]:
        """Return a summary of all hooks for display."""
        return [
            {
                "name": h.name,
                "event": h.event.value,
                "command": h.command,
                "enabled": h.enabled,
                "timeout": h.timeout,
            }
            for h in self._hooks
        ]
