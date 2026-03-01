"""Tests for the cascade theme system."""

from cascade.ui.theme import (
    ColorPalette,
    ProviderTheme,
    CascadeTheme,
    DEFAULT_THEME,
    PROVIDER_THEMES,
    CYAN,
    VIOLET,
    DARK_BG,
    LIGHT_TEXT,
    THEME,
    console,
    render_header,
    render_footer,
    render_divider,
)


class TestColorPalette:
    def test_defaults(self):
        p = ColorPalette()
        assert p.bg == "#0c0c10"
        assert p.error == "#e55a6e"
        assert p.diff_add == "#34d399"

    def test_frozen(self):
        p = ColorPalette()
        try:
            p.bg = "#ffffff"
            assert False, "should be frozen"
        except AttributeError:
            pass


class TestProviderTheme:
    def test_fields(self):
        pt = ProviderTheme(
            name="test", accent="#ff0000", abbreviation="tst",
            mode="dev", label="dev mode",
        )
        assert pt.name == "test"
        assert pt.abbreviation == "tst"

    def test_frozen(self):
        pt = PROVIDER_THEMES["claude"]
        try:
            pt.accent = "#000000"
            assert False, "should be frozen"
        except AttributeError:
            pass


class TestCascadeTheme:
    def test_get_provider_known(self):
        theme = DEFAULT_THEME
        pt = theme.get_provider("gemini")
        assert pt.name == "gemini"
        assert pt.accent == "#b44dff"
        assert pt.abbreviation == "gem"

    def test_get_provider_unknown_fallback(self):
        theme = DEFAULT_THEME
        pt = theme.get_provider("unknown_provider")
        assert pt.name == "unknown_provider"
        assert pt.abbreviation == "unk"
        assert pt.mode == "chat"

    def test_all_providers_present(self):
        for name in ("claude", "gemini", "openai", "openrouter"):
            assert name in DEFAULT_THEME.providers


class TestBackwardCompat:
    def test_legacy_constants_exist(self):
        assert isinstance(CYAN, str)
        assert isinstance(VIOLET, str)
        assert isinstance(DARK_BG, str)
        assert isinstance(LIGHT_TEXT, str)

    def test_theme_dict(self):
        assert "primary" in THEME
        assert "error" in THEME

    def test_console_is_console(self):
        from rich.console import Console
        assert isinstance(console, Console)

    def test_render_helpers_callable(self):
        assert callable(render_header)
        assert callable(render_footer)
        assert callable(render_divider)
