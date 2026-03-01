"""Tests for cascade.ui.input_container."""

from io import StringIO

from rich.console import Console

from cascade.ui.input_container import (
    build_prompt_prefix,
    print_input_bottom,
    print_input_top,
    print_mode_indicator,
)
from cascade.ui.theme import DEFAULT_THEME


def _capture_console() -> Console:
    return Console(file=StringIO(), width=80, force_terminal=True)


def test_print_input_top():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("claude")
    print_input_top(theme, 1000, con)
    output = con.file.getvalue()
    assert "\u256d" in output
    assert "claude" in output


def test_print_input_bottom():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("claude")
    print_input_bottom(theme, con)
    output = con.file.getvalue()
    assert "\u2570" in output


def test_build_prompt_prefix():
    theme = DEFAULT_THEME.get_provider("claude")
    prefix = build_prompt_prefix(theme)
    assert isinstance(prefix, list)
    assert len(prefix) == 2
    # Prompt char is U+276F
    assert "\u276f" in prefix[1][1]


def test_print_input_top_no_tokens():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("gemini")
    print_input_top(theme, 0, con)
    output = con.file.getvalue()
    assert "\u256d" in output
    assert "gemini" in output


def test_print_input_top_large_tokens():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("openai")
    print_input_top(theme, 1_500_000, con)
    output = con.file.getvalue()
    assert "1.5M" in output


def test_print_mode_indicator():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("gemini")
    print_mode_indicator(theme, "design", con)
    output = con.file.getvalue()
    assert "\u25b8\u25b8" in output
    assert "design" in output
    assert "shift+tab" in output


def test_token_format_zero():
    con = _capture_console()
    theme = DEFAULT_THEME.get_provider("claude")
    print_input_top(theme, 0, con)
    output = con.file.getvalue()
    assert "~0 tokens" in output
