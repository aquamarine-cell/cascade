"""Gutter-based response rendering.

Every output line is prefixed with a 6-char gutter showing the provider
abbreviation on the first line and a continuation pipe on subsequent lines.
"""

from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.text import Text

from .theme import DEFAULT_THEME, ProviderTheme

GUTTER_WIDTH = 6


def _make_gutter(label: str, accent: str, pad: bool = False) -> Text:
    """Build a gutter cell: 'cla | ' or '    | '."""
    t = Text()
    if pad:
        t.append(" " * 4, style="")
    else:
        t.append(f"{label:<4}", style=f"bold {accent}")
    t.append("| ", style=f"dim {DEFAULT_THEME.palette.text_muted}")
    return t


def render_gutter_line(
    content: Text,
    abbreviation: str,
    accent: str,
    first: bool = True,
) -> Text:
    """Render a single line through the gutter.

    Args:
        content: Rich Text for the line body.
        abbreviation: 3-char provider abbreviation (shown on first line only).
        accent: Hex color for the abbreviation.
        first: Whether this is the first line of the block.
    """
    gutter = _make_gutter(abbreviation if first else "", accent, pad=not first)
    gutter.append_text(content)
    return gutter


def render_user_gutter(text: str, console: Console) -> None:
    """Print a user message with 'you | ' gutter prefix."""
    palette = DEFAULT_THEME.palette
    lines = text.split("\n")
    for i, line in enumerate(lines):
        gutter = _make_gutter("you" if i == 0 else "", palette.text_bright, pad=i > 0)
        gutter.append(line, style=palette.text_bright)
        console.print(gutter)


def render_response_block(
    lines: list[Text],
    theme: ProviderTheme,
    console: Console,
) -> None:
    """Render a complete multi-line response through the gutter.

    Args:
        lines: List of Rich Text objects, one per output line.
        theme: Provider theme for accent/abbreviation.
        console: Rich Console instance.
    """
    for i, line_text in enumerate(lines):
        guttered = render_gutter_line(
            line_text,
            abbreviation=theme.abbreviation,
            accent=theme.accent,
            first=(i == 0),
        )
        console.print(guttered)


def render_bookmark(
    label: Optional[str] = None,
    console: Optional[Console] = None,
) -> None:
    """Print a horizontal bookmark divider with an optional centered label.

    Uses box-drawing chars: thin horizontal line with the label (or timestamp)
    centered in the gutter-indented area.
    """
    from .theme import console as default_console

    con = console or default_console
    palette = DEFAULT_THEME.palette
    width = con.width or 80
    inner_width = width - GUTTER_WIDTH

    if label is None:
        label = datetime.now().strftime("%H:%M")

    # Build: '    |---- label ----'
    pad = max((inner_width - len(label) - 2) // 2, 1)
    rule_char = "\u2500"
    line = Text()
    line.append(" " * 4, style="")
    line.append("| ", style=f"dim {palette.text_muted}")
    line.append(rule_char * pad, style=f"dim {palette.text_muted}")
    line.append(f" {label} ", style=f"dim {palette.text_dim}")
    line.append(rule_char * pad, style=f"dim {palette.text_muted}")
    con.print(line)
