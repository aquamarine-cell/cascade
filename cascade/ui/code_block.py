"""Bordered code block container with syntax highlighting.

Renders fenced code blocks in box-drawing borders, indented by GUTTER_WIDTH
to align within the response gutter.
"""

from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text

from .gutter import GUTTER_WIDTH
from .theme import DEFAULT_THEME

_TOP_LEFT = "\u256d"
_TOP_RIGHT = "\u256e"
_BOT_LEFT = "\u2570"
_BOT_RIGHT = "\u256f"
_VERT = "\u2502"
_HORIZ = "\u2500"


def render_code_container(
    code: str,
    language: str = "",
    console: Console | None = None,
) -> None:
    """Render a bordered code block with syntax highlighting.

    Args:
        code: The code string (without fences).
        language: Language hint for syntax highlighting.
        console: Rich Console to print to.
    """
    from .theme import console as default_console

    con = console or default_console
    palette = DEFAULT_THEME.palette
    indent = " " * GUTTER_WIDTH

    # Determine inner width
    term_width = con.width or 80
    inner_width = term_width - GUTTER_WIDTH - 4  # 4 = border + padding

    lang_label = language or "text"

    # Top border: indent + corner + lang label + dashes + corner
    top_content_width = inner_width - len(lang_label) - 1
    top = Text()
    top.append(indent)
    top.append(_TOP_LEFT, style=f"dim {palette.border}")
    top.append(f" {lang_label} ", style=f"dim {palette.text_dim}")
    top.append(_HORIZ * max(top_content_width - 2, 1), style=f"dim {palette.border}")
    top.append(_TOP_RIGHT, style=f"dim {palette.border}")
    con.print(top)

    # Syntax-highlighted code lines
    lines = code.rstrip("\n").split("\n")
    for i, line in enumerate(lines):
        row = Text()
        row.append(indent)
        row.append(f"{_VERT} ", style=f"dim {palette.border}")

        # Line number
        line_num = f"{i + 1:>3} "
        row.append(line_num, style=f"{palette.text_muted}")

        # Syntax highlight the line via Rich Syntax
        try:
            syn = Syntax(
                line,
                language or "text",
                theme="monokai",
                line_numbers=False,
                word_wrap=False,
            )
            # Extract highlighted text from Syntax
            highlighted = syn.highlight(line)
            row.append_text(highlighted)
        except Exception:
            row.append(line, style=palette.text)

        con.print(row, overflow="ellipsis", no_wrap=True)

    # Bottom border
    bot = Text()
    bot.append(indent)
    bot.append(_BOT_LEFT, style=f"dim {palette.border}")
    bot.append(_HORIZ * (inner_width + 1), style=f"dim {palette.border}")
    bot.append(_BOT_RIGHT, style=f"dim {palette.border}")
    con.print(bot)
