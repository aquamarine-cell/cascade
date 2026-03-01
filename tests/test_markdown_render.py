"""Tests for cascade.ui.markdown."""

from cascade.ui.markdown import render_markdown_line


def test_plain_text():
    result = render_markdown_line("hello world")
    assert "hello world" in result.plain


def test_inline_code():
    result = render_markdown_line("use `foo` here")
    assert "foo" in result.plain


def test_bold():
    result = render_markdown_line("this is **bold** text")
    assert "bold" in result.plain


def test_italic():
    result = render_markdown_line("this is *italic* text")
    assert "italic" in result.plain


def test_header_h1():
    result = render_markdown_line("# Big Title")
    assert "Big Title" in result.plain


def test_header_h2():
    result = render_markdown_line("## Subtitle")
    assert "Subtitle" in result.plain


def test_header_h3():
    result = render_markdown_line("### Minor")
    assert "Minor" in result.plain


def test_bullet_list():
    result = render_markdown_line("- item one")
    assert "item one" in result.plain


def test_numbered_list():
    result = render_markdown_line("1. first item")
    assert "first item" in result.plain


def test_link():
    result = render_markdown_line("see [docs](https://example.com)")
    assert "docs" in result.plain


def test_multiple_inline_codes():
    result = render_markdown_line("`a` and `b`")
    assert "a" in result.plain
    assert "b" in result.plain


def test_empty_line():
    result = render_markdown_line("")
    assert result.plain == ""


def test_indented_bullet():
    result = render_markdown_line("  - nested")
    assert "nested" in result.plain
