"""Load per-project configuration from .cascade/ directories.

Directory convention:
    .cascade/
        system_prompt.md       - Injected as system prompt for all conversations
        agents.yaml            - Per-agent overrides (provider, model, temperature, system_prompt)
        permissions.yaml       - Tool/plugin permissions
        context/               - Files auto-loaded into conversation context
            architecture.md
            design.md
"""

from pathlib import Path
from typing import Optional

import yaml


class ProjectContext:
    """Discover and load a project's .cascade/ directory."""

    def __init__(self, start_dir: Optional[str] = None):
        self.start_dir = Path(start_dir or ".").resolve()
        self.root = self._find_root()
        self.system_prompt = self._load_system_prompt()
        self.agents = self._load_yaml("agents.yaml")
        self.permissions = self._load_yaml("permissions.yaml")
        self.context_files = self._load_context_files()

    @property
    def found(self) -> bool:
        """True if a .cascade/ directory was found."""
        return self.root is not None

    def _find_root(self) -> Optional[Path]:
        """Walk up from start_dir to find the nearest .cascade/ directory."""
        current = self.start_dir
        for _ in range(50):  # safety limit
            candidate = current / ".cascade"
            if candidate.is_dir():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent
        return None

    def _load_system_prompt(self) -> str:
        """Load system_prompt.md if it exists."""
        if self.root is None:
            return ""
        path = self.root / "system_prompt.md"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return ""

    def _load_yaml(self, filename: str) -> dict:
        """Load a YAML file from .cascade/ if it exists."""
        if self.root is None:
            return {}
        path = self.root / filename
        if not path.is_file():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _load_context_files(self) -> dict[str, str]:
        """Load all files from .cascade/context/ into a dict of name -> content."""
        if self.root is None:
            return {}
        context_dir = self.root / "context"
        if not context_dir.is_dir():
            return {}
        files = {}
        for path in sorted(context_dir.iterdir()):
            if path.is_file() and not path.name.startswith("."):
                try:
                    files[path.name] = path.read_text(encoding="utf-8")
                except Exception:
                    continue
        return files

    def get_full_system_prompt(self) -> str:
        """Build a complete system prompt including context files."""
        parts = []
        if self.system_prompt:
            parts.append(self.system_prompt)
        if self.context_files:
            parts.append("\n--- Reference Materials ---\n")
            for name, content in self.context_files.items():
                parts.append(f"### {name}\n{content}\n")
        return "\n\n".join(parts)

    def summary(self) -> str:
        """Short summary for display in banner/status."""
        if not self.found:
            return "No project context"
        items = []
        if self.system_prompt:
            items.append("system prompt")
        if self.agents:
            items.append(f"{len(self.agents)} agent(s)")
        if self.context_files:
            items.append(f"{len(self.context_files)} context file(s)")
        return f"Project: {', '.join(items)}" if items else "Project: (empty .cascade/)"
