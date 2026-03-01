"""Project scaffolding for .cascade/ directories.

Creates the directory structure and writes template files based on
the detected or chosen project type.
"""

from pathlib import Path
from typing import Callable, Optional

import yaml

from .templates import detect_project_type, get_template


def run_init(
    path: Path,
    project_type: str,
    print_fn: Optional[Callable[[str], None]] = None,
    *,
    enable_system_prompt: bool = True,
    enable_agents: bool = True,
    enable_context: bool = True,
) -> str:
    """Scaffold a .cascade/ project directory.

    Args:
        path: Project root directory.
        project_type: One of the known project types (python, web, etc.).
        print_fn: Optional callback for progress messages.
        enable_system_prompt: Write system_prompt.md from template.
        enable_agents: Write agents.yaml from template.
        enable_context: Create the context/ subdirectory.

    Returns:
        A summary string of what was created/skipped.
    """
    path = path.resolve()
    cascade_dir = path / ".cascade"
    template = get_template(project_type)

    created: list[str] = []
    skipped: list[str] = []

    def _log(msg: str) -> None:
        if print_fn:
            print_fn(msg)

    # Create .cascade/ root
    if not cascade_dir.is_dir():
        cascade_dir.mkdir(parents=True, exist_ok=True)
        created.append(".cascade/")
    else:
        skipped.append(".cascade/ (already exists)")

    # system_prompt.md
    if enable_system_prompt:
        sp_path = cascade_dir / "system_prompt.md"
        if sp_path.exists():
            skipped.append("system_prompt.md (already exists)")
            _log("  skipped: system_prompt.md (already exists)")
        else:
            sp_path.write_text(template["system_prompt"] + "\n", encoding="utf-8")
            created.append("system_prompt.md")
            _log("  created: system_prompt.md")

    # agents.yaml (agents + workflows merged)
    if enable_agents:
        agents_path = cascade_dir / "agents.yaml"
        if agents_path.exists():
            skipped.append("agents.yaml (already exists)")
            _log("  skipped: agents.yaml (already exists)")
        else:
            agents_data = dict(template.get("agents", {}))
            workflows = template.get("workflows")
            if workflows:
                agents_data["workflows"] = dict(workflows)
            verify = template.get("verify")
            if verify:
                agents_data.setdefault("workflows", {})
                agents_data["workflows"]["verify"] = dict(verify)
            agents_path.write_text(
                yaml.dump(agents_data, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )
            created.append("agents.yaml")
            _log("  created: agents.yaml")

    # context/ directory
    if enable_context:
        ctx_dir = cascade_dir / "context"
        if ctx_dir.is_dir():
            skipped.append("context/ (already exists)")
            _log("  skipped: context/ (already exists)")
        else:
            ctx_dir.mkdir(parents=True, exist_ok=True)
            created.append("context/")
            _log("  created: context/")

    # Build summary
    lines = [f"Initialized .cascade/ for '{project_type}' project"]
    if created:
        lines.append(f"  created: {', '.join(created)}")
    if skipped:
        lines.append(f"  skipped: {', '.join(skipped)}")

    return "\n".join(lines)
