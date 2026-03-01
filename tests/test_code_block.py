"""Tests for cascade.ui.code_block."""

import re
from io import StringIO

from rich.console import Console

from cascade.ui.code_block import render_code_container


def _capture_console() -> Console:
    return Console(file=StringIO(), width=80, force_terminal=True)


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_renders_code():
    con = _capture_console()
    render_code_container("x = 1", "python", con)
    output = _strip_ansi(con.file.getvalue())
    assert "x = 1" in output
    assert "python" in output


def test_has_borders():
    con = _capture_console()
    render_code_container("print('hi')", "python", con)
    output = con.file.getvalue()
    assert "\u256d" in output
    assert "\u2570" in output


def test_multiline_code():
    con = _capture_console()
    code = "def foo():\n    return 42"
    render_code_container(code, "python", con)
    output = _strip_ansi(con.file.getvalue())
    assert "def foo" in output
    assert "return 42" in output


def test_line_numbers():
    con = _capture_console()
    render_code_container("a\nb\nc", "text", con)
    output = con.file.getvalue()
    assert "1" in output
    assert "2" in output
    assert "3" in output


def test_empty_code():
    con = _capture_console()
    render_code_container("", "text", con)
    # Should not crash


def test_no_language():
    con = _capture_console()
    render_code_container("hello", "", con)
    output = con.file.getvalue()
    assert "text" in output  # falls back to "text"
