"""Tests for cascade.ui.gutter."""

from io import StringIO

from rich.console import Console
from rich.text import Text

from cascade.ui.gutter import (
    GUTTER_WIDTH,
    render_bookmark,
    render_gutter_line,
    render_response_block,
    render_user_gutter,
)
from cascade.ui.theme import DEFAULT_THEME


def _capture_console() -> Console:
    return Console(file=StringIO(), width=80, force_terminal=True)


def test_gutter_width():
    assert GUTTER_WIDTH == 6


def test_render_gutter_line_first():
    content = Text("hello world")
    result = render_gutter_line(content, "cla", "#f0956c", first=True)
    plain = result.plain
    assert "cla" in plain
    assert "|" in plain
    assert "hello world" in plain


def test_render_gutter_line_continuation():
    content = Text("continued")
    result = render_gutter_line(content, "cla", "#f0956c", first=False)
    plain = result.plain
    assert "cla" not in plain
    assert "|" in plain
    assert "continued" in plain


def test_render_user_gutter():
    con = _capture_console()
    render_user_gutter("hello", con)
    output = con.file.getvalue()
    assert "you" in output
    assert "hello" in output


def test_render_user_gutter_multiline():
    con = _capture_console()
    render_user_gutter("line1\nline2", con)
    output = con.file.getvalue()
    assert "line1" in output
    assert "line2" in output


def test_render_response_block():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("claude")
    lines = [Text("first"), Text("second"), Text("third")]
    render_response_block(lines, theme, con)
    output = con.file.getvalue()
    assert "cla" in output
    assert "first" in output
    assert "second" in output
    assert "third" in output


def test_render_bookmark_default():
    con = _capture_console()
    render_bookmark(console=con)
    output = con.file.getvalue()
    # Should contain horizontal rule chars and a timestamp
    assert "\u2500" in output


def test_render_bookmark_custom_label():
    con = _capture_console()
    render_bookmark("test label", console=con)
    output = con.file.getvalue()
    assert "test label" in output
