"""Inline diff block for file write/edit operations.

Write block: amber accent, "> write path" header, full code.
Edit block: amber accent, "* edit path" header, red/green diff.
"""

from rich.text import Text
from rich.panel import Panel
from textual.widgets import Static

from ..theme import PALETTE


class DiffBlock(Static):
    """Inline diff viewer for file changes."""

    DEFAULT_CSS = """
    DiffBlock {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        file_path: str,
        diff_lines: list[tuple[int, str, str]],
        lines_changed: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._file_path = file_path
        self._diff_lines = diff_lines
        self._lines_changed = lines_changed

    def render(self) -> Panel:
        title = Text()
        title.append(" \u2727 edit ", style=f"bold {PALETTE.amber}")
        title.append(self._file_path, style=PALETTE.text_primary)

        subtitle = Text(f" {self._lines_changed} lines changed ", style=f"dim {PALETTE.text_dim}")

        content = Text()
        for ln, op, line in self._diff_lines:
            if op == "-":
                content.append(f"{ln:>3}- ", style=f"bold {PALETTE.diff_del}")
                content.append(f"{line}\n", style=f"strikethrough {PALETTE.diff_del}")
            elif op == "+":
                content.append(f"{ln:>3}+ ", style=f"bold {PALETTE.diff_add}")
                content.append(f"{line}\n", style=f"bold {PALETTE.diff_add}")
            else:
                content.append(f"{ln:>3}  ", style=f"dim {PALETTE.text_dim}")
                content.append(f"{line}\n", style=PALETTE.text_primary)

        return Panel(
            content,
            title=title,
            title_align="left",
            subtitle=subtitle,
            subtitle_align="right",
            border_style=f"{PALETTE.amber} 40%",
            background=PALETTE.code_bg,
            padding=(0, 1),
            expand=True,
        )


class WriteBlock(Static):
    """Block showing a full file write (new file creation)."""

    DEFAULT_CSS = """
    WriteBlock {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self, file_path: str, code: str, language: str = "text", **kwargs) -> None:
        super().__init__(**kwargs)
        self._file_path = file_path
        self._code = code
        self._language = language

    def render(self) -> Panel:
        from rich.syntax import Syntax

        title = Text()
        title.append(" > write ", style=f"bold {PALETTE.amber}")
        title.append(self._file_path, style=PALETTE.text_primary)

        subtitle = Text(" new file ", style=f"dim {PALETTE.text_dim}")

        syntax = Syntax(
            self._code,
            self._language,
            theme="monokai",
            line_numbers=True,
            word_wrap=False,
            background_color=PALETTE.code_bg,
        )

        return Panel(
            syntax,
            title=title,
            title_align="left",
            subtitle=subtitle,
            subtitle_align="right",
            border_style=f"{PALETTE.amber} 40%",
            background=PALETTE.code_bg,
            padding=(0, 1),
            expand=True,
        )
