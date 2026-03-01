"""Bottom status bar for prompt_toolkit.

Left: ~/path · branch*
Right: colored dots per provider with token counts.
"""

import subprocess
from pathlib import Path

from prompt_toolkit.formatted_text import HTML

from .theme import DEFAULT_THEME, PROVIDER_THEMES


def _git_branch() -> str:
    """Get current git branch, or empty string if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        branch = result.stdout.strip()
        if branch:
            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            dirty = "*" if status.stdout.strip() else ""
            return f"{branch}{dirty}"
    except Exception:
        pass
    return ""


def _shorten_path(path: str) -> str:
    """Shorten path by replacing home dir with ~."""
    home = str(Path.home())
    if path.startswith(home):
        return "~" + path[len(home):]
    return path


def build_status_bar(
    provider_tokens: dict[str, int] | None = None,
) -> HTML:
    """Build prompt_toolkit HTML for the bottom toolbar.

    Args:
        provider_tokens: Mapping of provider_name -> total tokens used.

    Returns:
        HTML formatted text for prompt_toolkit's bottom_toolbar.
    """
    import os

    cwd = _shorten_path(os.getcwd())
    branch = _git_branch()

    left = f" {cwd}"
    if branch:
        left += f" \u00b7 {branch}"

    # Right side: per-provider token dots
    right_parts = []
    tokens = provider_tokens or {}
    for name, theme in PROVIDER_THEMES.items():
        count = tokens.get(name, 0)
        if count > 0:
            label = _format_short(count)
        else:
            label = "0"
        right_parts.append(
            f'<style fg="{theme.accent}">\u25cf</style> {label}'
        )

    right = "  ".join(right_parts)

    return HTML(f" <b>{left}</b>    {right} ")


def _format_short(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)
