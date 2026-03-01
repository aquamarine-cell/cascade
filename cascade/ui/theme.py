"""Cascade theme system: palette, provider themes, and backward-compat shims."""

from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


@dataclass(frozen=True)
class ColorPalette:
    """Core UI color palette."""

    bg: str = "#0c0c10"
    surface: str = "#121218"
    border: str = "#222233"
    border_subtle: str = "#1a1a28"
    text_bright: str = "#e8e8f0"
    text: str = "#b8b8cc"
    text_dim: str = "#4a4a60"
    text_muted: str = "#363648"
    inline_code: str = "#00d4e5"
    file_ops: str = "#e5c747"
    diff_add: str = "#34d399"
    diff_del: str = "#e55a6e"
    error: str = "#e55a6e"
    spinner: str = "#e5c747"
    syntax_keyword: str = "#5a9cf0"
    syntax_string: str = "#34d399"
    syntax_builtin: str = "#00d4e5"
    syntax_self: str = "#e55a6e"
    syntax_class: str = "#e5c747"


@dataclass(frozen=True)
class ProviderTheme:
    """Visual identity for a single provider."""

    name: str
    accent: str
    abbreviation: str
    mode: str
    label: str


# Provider visual identities
PROVIDER_THEMES: dict[str, ProviderTheme] = {
    "claude": ProviderTheme(
        name="claude",
        accent="#f0956c",
        abbreviation="cla",
        mode="plan",
        label="plan mode",
    ),
    "gemini": ProviderTheme(
        name="gemini",
        accent="#b44dff",
        abbreviation="gem",
        mode="design",
        label="design mode",
    ),
    "openai": ProviderTheme(
        name="openai",
        accent="#34d399",
        abbreviation="cdx",
        mode="build",
        label="build mode",
    ),
    "openrouter": ProviderTheme(
        name="openrouter",
        accent="#d94060",
        abbreviation="ort",
        mode="test",
        label="test mode",
    ),
}


@dataclass(frozen=True)
class CascadeTheme:
    """Complete theme binding palette + provider themes."""

    palette: ColorPalette
    providers: dict[str, ProviderTheme]

    def get_provider(self, name: str) -> ProviderTheme:
        """Look up a provider theme by name, with a neutral fallback."""
        return self.providers.get(name, ProviderTheme(
            name=name,
            accent=self.palette.text_dim,
            abbreviation=name[:3],
            mode="chat",
            label="chat mode",
        ))


DEFAULT_THEME = CascadeTheme(
    palette=ColorPalette(),
    providers=PROVIDER_THEMES,
)

# ---------------------------------------------------------------------------
# Backward-compat shims -- existing code imports these module-level names.
# DEPRECATED: prefer DEFAULT_THEME.palette.* in new code.
# ---------------------------------------------------------------------------

CYAN = "#00d4e5"
VIOLET = "#b44dff"
DARK_BG = DEFAULT_THEME.palette.bg
LIGHT_TEXT = DEFAULT_THEME.palette.text_bright

THEME = {
    "primary": CYAN,
    "secondary": VIOLET,
    "bg": DARK_BG,
    "text": LIGHT_TEXT,
    "accent": DEFAULT_THEME.palette.diff_add,
    "error": DEFAULT_THEME.palette.error,
}

console = Console()


# ---------------------------------------------------------------------------
# Legacy render helpers -- still used by cli.py and elsewhere.
# ---------------------------------------------------------------------------

def render_header(title: str, subtitle: str = "") -> None:
    """Render a header panel."""
    header_text = Text(title, style=f"bold {CYAN}")
    if subtitle:
        header_text.append(f"\n{subtitle}", style=f"dim {LIGHT_TEXT}")
    panel = Panel(
        header_text,
        border_style=VIOLET,
        padding=(1, 2),
        expand=False,
    )
    console.print(panel)


def render_footer(text: str, provider: str = "") -> None:
    """Render footer with provider info."""
    footer_text = Text(text, style=f"dim {LIGHT_TEXT}")
    if provider:
        footer_text.append(f" . {provider}", style=f"dim {CYAN}")
    console.print(footer_text)


def render_divider() -> None:
    """Render a styled divider."""
    console.print(Text("\u2500" * 80, style=f"dim {VIOLET}"))
