"""Parse hook definitions from configuration data."""

from typing import Any

from .runner import HookDefinition, HookEvent


_EVENT_MAP = {
    "before_ask": HookEvent.BEFORE_ASK,
    "after_response": HookEvent.AFTER_RESPONSE,
    "on_exit": HookEvent.ON_EXIT,
    "on_error": HookEvent.ON_ERROR,
}


def load_hooks_from_config(hooks_data: list[dict[str, Any]]) -> tuple[HookDefinition, ...]:
    """Parse a list of hook config dicts into HookDefinition instances.

    Each dict should have:
        name: str (required)
        event: str (required) - one of before_ask, after_response, on_exit, on_error
        command: str (required)
        timeout: int (optional, default 30)
        enabled: bool (optional, default True)

    Invalid entries are silently skipped.
    """
    hooks = []

    for entry in hooks_data:
        if not isinstance(entry, dict):
            continue

        name = entry.get("name")
        event_str = entry.get("event")
        command = entry.get("command")

        if not all((name, event_str, command)):
            continue

        event = _EVENT_MAP.get(event_str)
        if event is None:
            continue

        hooks.append(HookDefinition(
            name=name,
            event=event,
            command=command,
            timeout=entry.get("timeout", 30),
            enabled=entry.get("enabled", True),
        ))

    return tuple(hooks)
