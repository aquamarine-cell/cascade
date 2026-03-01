"""Tests for the ghost table provider display."""

from unittest.mock import MagicMock

from cascade.ui.ghost_table import render_ghost_table
from cascade.providers.base import ProviderConfig


def _make_provider(model: str = "test-model"):
    prov = MagicMock()
    prov.config = ProviderConfig(api_key="k", model=model)
    return prov


class TestGhostTable:
    def test_empty_providers(self, capsys):
        render_ghost_table({}, "")
        out = capsys.readouterr().out
        assert "PROVIDER" in out
        assert "none" in out.lower() or "no providers" in out.lower()

    def test_active_row_shows_active(self, capsys):
        providers = {"gemini": _make_provider("gemini-2.5-flash")}
        render_ghost_table(providers, "gemini")
        out = capsys.readouterr().out
        assert "gemini" in out
        assert "active" in out

    def test_inactive_row_muted(self, capsys):
        providers = {
            "gemini": _make_provider("gemini-2.5-flash"),
            "claude": _make_provider("claude-sonnet-4-20250514"),
        }
        render_ghost_table(providers, "gemini")
        out = capsys.readouterr().out
        assert "gemini" in out
        assert "claude" in out

    def test_header_columns(self, capsys):
        render_ghost_table({"x": _make_provider()}, "x")
        out = capsys.readouterr().out
        assert "PROVIDER" in out
        assert "MODEL" in out
        assert "STATUS" in out

    def test_multiple_providers_sorted(self, capsys):
        providers = {
            "openai": _make_provider("gpt-4o"),
            "claude": _make_provider("claude-sonnet"),
            "gemini": _make_provider("gemini-flash"),
        }
        render_ghost_table(providers, "claude")
        out = capsys.readouterr().out
        # claude should come before gemini alphabetically
        assert out.index("claude") < out.index("gemini")
