"""Tests for the pyfiglet ASCII art banner."""

from rich.text import Text

from cascade.ui.banner import render_banner, _lerp_color, GRADIENT


def test_render_banner_returns_text():
    """render_banner should return a Rich Text object."""
    result = render_banner()
    assert isinstance(result, Text)


def test_render_banner_default_word():
    """Default word is CASCADE."""
    result = render_banner()
    plain = result.plain
    lines = plain.split("\n")
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) >= 3, "Banner should have at least 3 non-empty rows"


def test_render_banner_contains_art_chars():
    """Banner should contain box-drawing or block characters from figlet."""
    result = render_banner()
    plain = result.plain
    # ansi_shadow uses block chars and box-drawing chars
    art_chars = set("\u2588\u2580\u2584\u2554\u2557\u255a\u255d\u2551\u2550\u2560\u2563\u256c\u2569\u2566")
    has_art = any(ch in art_chars for ch in plain)
    assert has_art, "Banner should use figlet art characters"


def test_render_banner_custom_word():
    """render_banner should accept a custom word."""
    result = render_banner("CASE")
    assert isinstance(result, Text)
    assert len(result.plain) > 0


def test_lerp_color_boundaries():
    """Interpolation at 0 and 1 should return first and last stops."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    assert _lerp_color(colors, 0.0) == (255, 0, 0)
    assert _lerp_color(colors, 1.0) == (0, 0, 255)


def test_lerp_color_midpoint():
    """Interpolation at 0.5 should return the middle stop."""
    colors = [(0, 0, 0), (100, 100, 100), (200, 200, 200)]
    result = _lerp_color(colors, 0.5)
    assert result == (100, 100, 100)


def test_gradient_has_colors():
    """Gradient should have multiple color stops."""
    assert len(GRADIENT) >= 3


def test_banner_fits_80_columns():
    """Banner should fit within 80 columns."""
    result = render_banner()
    for line in result.plain.split("\n"):
        assert len(line) <= 80, f"Line too wide ({len(line)} chars): {line!r}"
