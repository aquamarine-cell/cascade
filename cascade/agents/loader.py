"""Load AgentDef instances from the dict already parsed by ProjectContext."""

from typing import Any

from .schema import AgentDef


def load_agents_from_dict(data: dict[str, Any]) -> dict[str, AgentDef]:
    """Parse agent definitions from a YAML-loaded dict.

    Expected format (top-level keys are agent names)::

        planner:
          description: "Plan features"
          provider: claude
          model: claude-opus-4-6
          system_prompt: "You are a planning assistant."
          allowed_tools:
            - read_file
            - write_file

    The special ``workflows`` key is skipped (handled separately).
    Invalid entries are silently skipped.
    """
    agents: dict[str, AgentDef] = {}

    for name, entry in data.items():
        if name == "workflows":
            continue
        if not isinstance(entry, dict):
            continue
        try:
            allowed = entry.get("allowed_tools")
            if allowed is not None:
                allowed = tuple(str(t) for t in allowed)

            agents[name] = AgentDef(
                name=name,
                description=str(entry.get("description", "")),
                provider=entry.get("provider"),
                model=entry.get("model"),
                temperature=entry.get("temperature"),
                system_prompt=str(entry.get("system_prompt", "")),
                allowed_tools=allowed,
                max_tokens=entry.get("max_tokens"),
            )
        except Exception:
            continue

    return agents
