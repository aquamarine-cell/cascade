"""Tests for cascade.ui.stream."""

import re
from io import StringIO

from rich.console import Console

from cascade.ui.stream import StreamRenderer
from cascade.ui.theme import DEFAULT_THEME


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _capture_console() -> Console:
    return Console(file=StringIO(), width=80, force_terminal=True)


def _make_renderer(con: Console | None = None) -> tuple[StreamRenderer, Console]:
    con = con or _capture_console()
    theme = DEFAULT_THEME.get_provider("claude")
    return StreamRenderer(theme, con), con


def test_simple_prose():
    renderer, con = _make_renderer()
    renderer.feed("hello world\n")
    renderer.finish()
    output = con.file.getvalue()
    assert "hello world" in output
    assert "cla" in output


def test_multiline_prose():
    renderer, con = _make_renderer()
    renderer.feed("line one\nline two\nline three\n")
    renderer.finish()
    output = con.file.getvalue()
    assert "line one" in output
    assert "line two" in output
    assert "line three" in output


def test_code_block():
    renderer, con = _make_renderer()
    renderer.feed("```python\nprint('hi')\n```\n")
    renderer.finish()
    output = con.file.getvalue()
    assert "python" in output
    assert "print" in output


def test_mixed_prose_and_code():
    renderer, con = _make_renderer()
    renderer.feed("Before code:\n```js\nconsole.log(1)\n```\nAfter code.\n")
    renderer.finish()
    output = _strip_ansi(con.file.getvalue())
    assert "Before code" in output
    assert "console" in output
    assert "After code" in output


def test_chunked_input():
    """Test that arbitrary chunk boundaries are handled correctly."""
    renderer, con = _make_renderer()
    # Split "hello\n" across multiple chunks
    renderer.feed("hel")
    renderer.feed("lo\n")
    renderer.finish()
    output = con.file.getvalue()
    assert "hello" in output


def test_chunked_code_fence():
    """Test code fence split across chunks."""
    renderer, con = _make_renderer()
    renderer.feed("``")
    renderer.feed("`py")
    renderer.feed("thon\nx=1\n")
    renderer.feed("``")
    renderer.feed("`\n")
    renderer.finish()
    output = con.file.getvalue()
    assert "python" in output


def test_unterminated_code_block():
    """Unterminated code blocks should still render on finish()."""
    renderer, con = _make_renderer()
    renderer.feed("```python\nx=1\n")
    renderer.finish()
    output = _strip_ansi(con.file.getvalue())
    assert "x" in output
    assert "1" in output


def test_empty_input():
    renderer, con = _make_renderer()
    renderer.feed("")
    renderer.finish()
    # Should not crash


def test_first_line_flag():
    renderer, con = _make_renderer()
    assert renderer.is_first_line is True
    renderer.feed("first\n")
    assert renderer.is_first_line is False
