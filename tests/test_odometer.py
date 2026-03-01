"""Tests for cascade.ui.odometer."""

from io import StringIO

from rich.console import Console

from cascade.ui.odometer import render_exit_summary


def _capture_console() -> Console:
    return Console(file=StringIO(), width=60, force_terminal=True)


def test_renders_summary():
    con = _capture_console()
    render_exit_summary(
        session_id="abc123",
        messages=5,
        responses=5,
        input_tokens=1000,
        output_tokens=2000,
        wall_time="1m 30s",
        provider="claude",
        model="claude-3.5-sonnet",
        console=con,
        animate=False,
    )
    output = con.file.getvalue()
    assert "abc123" in output
    assert "5 sent" in output
    assert "1m 30s" in output
    assert "claude" in output


def test_renders_borders():
    con = _capture_console()
    render_exit_summary(
        session_id="x",
        messages=0,
        responses=0,
        input_tokens=0,
        output_tokens=0,
        wall_time="0s",
        provider="gemini",
        model="gemini-2.5-pro",
        console=con,
        animate=False,
    )
    output = con.file.getvalue()
    assert "\u256d" in output
    assert "\u2570" in output
    assert "session summary" in output


def test_provider_tokens():
    con = _capture_console()
    render_exit_summary(
        session_id="t",
        messages=1,
        responses=1,
        input_tokens=100,
        output_tokens=200,
        wall_time="5s",
        provider="claude",
        model="claude-3.5-sonnet",
        provider_tokens={"claude": 200, "gemini": 50},
        console=con,
        animate=False,
    )
    output = con.file.getvalue()
    assert "cla" in output
