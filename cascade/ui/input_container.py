"""Floating input container with box-drawing borders.

Spec: rounded corners, provider name top-left in accent, token count
top-right in text-muted, prompt char is U+276F in accent color,
border in dim provider accent.
"""

from rich.console import Console
from rich.text import Text

from .theme import DEFAULT_THEME, ProviderTheme

_TOP_LEFT = "\u256d"
_TOP_RIGHT = "\u256e"
_BOT_LEFT = "\u2570"
_BOT_RIGHT = "\u256f"
_VERT = "\u2502"
_HORIZ = "\u2500"
_PROMPT_CHAR = "\u276f"  # heavy right-pointing angle quotation mark


def print_input_top(
    theme: ProviderTheme,
    token_count: int = 0,
    console: Console | None = None,
) -> None:
    """Print the top border of the floating input container.

    Format: ╭─ provider ─────────────── ~N tokens ─╮
    """
    from .theme import console as default_console

    con = console or default_console
    palette = DEFAULT_THEME.palette
    width = con.width or 80

    border_style = f"dim {theme.accent}"
    left_label = f" {theme.name} "
    right_label = f" {_format_tokens(token_count)} "

    # Width calculation: corner + dash + label + fill + right_label + dash + corner
    fill_width = width - 2 - 1 - len(left_label) - len(right_label) - 1

    line = Text()
    line.append(_TOP_LEFT, style=border_style)
    line.append(_HORIZ, style=border_style)
    line.append(left_label, style=f"bold {theme.accent}")
    line.append(_HORIZ * max(fill_width, 1), style=border_style)
    line.append(right_label, style=f"dim {palette.text_muted}")
    line.append(_HORIZ, style=border_style)
    line.append(_TOP_RIGHT, style=border_style)
    con.print(line)


def print_input_bottom(
    theme: ProviderTheme,
    console: Console | None = None,
) -> None:
    """Print the bottom border of the floating input container."""
    from .theme import console as default_console

    con = console or default_console
    width = con.width or 80
    border_style = f"dim {theme.accent}"

    line = Text()
    line.append(_BOT_LEFT, style=border_style)
    line.append(_HORIZ * (width - 2), style=border_style)
    line.append(_BOT_RIGHT, style=border_style)
    con.print(line)


def print_mode_indicator(
    theme: ProviderTheme,
    mode_name: str,
    console: Console | None = None,
) -> None:
    """Print the mode indicator below the input container.

    Format: ▸▸ design mode · shift+tab to cycle
    """
    from .theme import console as default_console

    con = console or default_console
    palette = DEFAULT_THEME.palette

    line = Text()
    line.append("  \u25b8\u25b8 ", style=f"{theme.accent}")
    line.append(mode_name, style=f"{theme.accent}")
    line.append(" mode \u00b7 shift+tab to cycle", style=f"dim {palette.text_dim}")
    con.print(line)


def build_prompt_prefix(theme: ProviderTheme) -> list[tuple[str, str]]:
    """Build prompt_toolkit formatted text for the input prefix.

    Renders as: '│ ❯ '
    """
    return [
        (f"fg:{DEFAULT_THEME.palette.text_muted}", f" {_VERT} "),
        (f"fg:{theme.accent} bold", f"{_PROMPT_CHAR} "),
    ]


def _format_tokens(count: int) -> str:
    if count >= 1_000_000:
        return f"~{count / 1_000_000:.1f}M tokens"
    if count >= 1000:
        return f"~{count / 1000:.1f}k tokens"
    return f"~{count} tokens"
