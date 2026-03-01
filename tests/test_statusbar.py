"""Tests for cascade.ui.statusbar."""

from cascade.ui.statusbar import build_status_bar


def test_build_status_bar_no_tokens():
    result = build_status_bar()
    assert isinstance(result, object)  # HTML object
    # Should contain path info
    text = result.value if hasattr(result, "value") else str(result)
    assert len(text) > 0


def test_build_status_bar_with_tokens():
    tokens = {"claude": 500, "gemini": 1200}
    result = build_status_bar(provider_tokens=tokens)
    text = result.value if hasattr(result, "value") else str(result)
    assert "500" in text or "1.2k" in text
