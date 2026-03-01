"""Tests for MainScreen helper behavior."""

from cascade.screens.main import summarize_user_prompt


def test_summarize_user_prompt_single_line_unchanged():
    text = "hello world"
    assert summarize_user_prompt(text) == text


def test_summarize_user_prompt_multiline_collapses():
    text = "line1\nline2\nline3\nline4"
    assert summarize_user_prompt(text) == "[pasted content 1 + 3 lines]"
