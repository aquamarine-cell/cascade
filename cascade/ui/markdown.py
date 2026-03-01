"""Single-line markdown renderer for inline styling.

Handles inline formatting only -- code blocks are routed through the
code_block module instead. Each line is converted to a Rich Text object.
"""

import re
from rich.text import Text

from .theme import DEFAULT_THEME

_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_HEADER = re.compile(r"^(#{1,6})\s+(.*)")


def render_markdown_line(line: str) -> Text:
    """Convert a single markdown line to styled Rich Text.

    Handles: inline code, bold, italic, headers, bullet lists, links.
    Does NOT handle fenced code blocks.
    """
    palette = DEFAULT_THEME.palette

    # Headers
    m = _HEADER.match(line)
    if m:
        level = len(m.group(1))
        header_text = m.group(2)
        t = Text()
        if level <= 2:
            t.append(header_text, style=f"bold {palette.text_bright}")
        else:
            t.append(header_text, style=f"bold {palette.text}")
        return t

    # Bullet lists: preserve indent, highlight bullet
    stripped = line.lstrip()
    if stripped.startswith(("- ", "* ", "+ ")):
        indent = len(line) - len(stripped)
        t = Text()
        t.append(" " * indent)
        t.append(stripped[0], style=f"{palette.text_dim}")
        rest = stripped[2:]
        t.append_text(_inline_format(f" {rest}", palette))
        return t

    # Numbered lists
    num_match = re.match(r"^(\s*\d+\.)\s+(.*)", line)
    if num_match:
        t = Text()
        t.append(num_match.group(1), style=f"{palette.text_dim}")
        t.append_text(_inline_format(f" {num_match.group(2)}", palette))
        return t

    return _inline_format(line, palette)


def _inline_format(text: str, palette) -> Text:
    """Apply inline formatting (code, bold, italic, links) to text."""
    result = Text()
    pos = 0

    # Merge all inline patterns with their positions
    spans = []
    for m in _INLINE_CODE.finditer(text):
        spans.append((m.start(), m.end(), "code", m.group(1)))
    for m in _BOLD.finditer(text):
        spans.append((m.start(), m.end(), "bold", m.group(1)))
    for m in _ITALIC.finditer(text):
        spans.append((m.start(), m.end(), "italic", m.group(1)))
    for m in _LINK.finditer(text):
        spans.append((m.start(), m.end(), "link", m.group(1)))

    # Sort by start position, filter overlapping
    spans.sort(key=lambda s: s[0])
    filtered = []
    last_end = 0
    for start, end, kind, content in spans:
        if start >= last_end:
            filtered.append((start, end, kind, content))
            last_end = end

    for start, end, kind, content in filtered:
        if start > pos:
            result.append(text[pos:start], style=palette.text)
        if kind == "code":
            result.append(f" {content} ", style=f"on {palette.surface} {palette.inline_code}")
        elif kind == "bold":
            result.append(content, style=f"bold {palette.text_bright}")
        elif kind == "italic":
            result.append(content, style=f"italic {palette.text}")
        elif kind == "link":
            result.append(content, style=f"underline {palette.inline_code}")
        pos = end

    if pos < len(text):
        result.append(text[pos:], style=palette.text)

    return result
