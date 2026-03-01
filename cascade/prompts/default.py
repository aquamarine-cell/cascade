"""Default system prompt for Cascade conversations.

Assembles identity, design language, quality gates, workflow instructions,
tool use guidance, and conventions into a single coherent system prompt.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional


DEFAULT_IDENTITY = (
    "You are Cascade, a multi-model AI assistant. "
    "For each proposed change imagine if it was the most elegant solution "
    "and had been designed that way since the start."
)

_QUALITY_GATES = """\
Quality Gates:
- Immutability: never mutate objects or arrays; create new instances
- Files under 800 lines, functions under 50 lines
- No hardcoded secrets; use environment variables
- Validate all user input at system boundaries
- Proper error handling with clear, user-friendly messages
- Security-first: parameterized queries, sanitized output, no leaked internals"""

_WORKFLOW = """\
Workflow:
- Decompose complex tasks into subtasks before acting
- Execute independent subtasks in parallel when possible
- Plan before executing; state your approach before writing code
- Follow TDD: write a failing test (RED), implement to pass (GREEN), refactor (REFACTOR)
- Prefer editing existing files over creating new ones"""

_TOOL_USE = """\
Tool Use:
- You have tools available. Use them proactively.
- Use the reflect tool when navigating difficulty, conflict, uncertainty, or endings.
- Report tool results honestly; never fabricate tool output."""

_CONVENTIONS = """\
Conventions:
- Use conventional commits: feat:, fix:, refactor:, docs:, test:, chore:
- No emojis in code, comments, or documentation
- Many small files over few large files
- Write clear, self-documenting code; add comments only where logic is non-obvious"""


def _find_design_md(
    explicit_path: Optional[str] = None,
    search_dirs: Optional[list[str]] = None,
) -> Optional[str]:
    """Locate design.md by searching common locations.

    Search order:
    1. Explicit path from config
    2. Provided search directories
    3. Current working directory
    4. Walk up to git root
    """
    if explicit_path:
        p = Path(explicit_path).expanduser()
        if p.is_file():
            return p.read_text(encoding="utf-8")

    candidates = list(search_dirs or [])
    candidates.append(str(Path.cwd()))

    # Walk up to find git root
    current = Path.cwd()
    for _ in range(50):
        if (current / ".git").exists():
            candidates.append(str(current))
            break
        parent = current.parent
        if parent == current:
            break
        current = parent

    for directory in candidates:
        path = Path(directory) / "design.md"
        if path.is_file():
            try:
                return path.read_text(encoding="utf-8")
            except Exception:
                continue

    return None


def build_default_prompt(
    include_design_language: bool = True,
    design_md_path: Optional[str] = None,
    current_date: Optional[str] = None,
) -> str:
    """Assemble the full default system prompt.

    Args:
        include_design_language: Whether to search for and include design.md.
        design_md_path: Explicit path to design.md.
        current_date: Override for the current date string.

    Returns:
        Complete system prompt string.
    """
    date_str = current_date or datetime.now().strftime("%Y-%m-%d")

    sections = [DEFAULT_IDENTITY, ""]

    if include_design_language:
        design_content = _find_design_md(explicit_path=design_md_path)
        if design_content:
            sections.append("Design Language:")
            sections.append(design_content.strip())
            sections.append("")

    sections.append(_QUALITY_GATES)
    sections.append("")
    sections.append(_WORKFLOW)
    sections.append("")
    sections.append(_TOOL_USE)
    sections.append("")
    sections.append(_CONVENTIONS)
    sections.append("")
    sections.append(f"Current date: {date_str}")

    return "\n".join(sections)
