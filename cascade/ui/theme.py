"""Deep Stream theme and styling."""

from rich.console import Console
from rich.style import Style
from rich.panel import Panel
from rich.text import Text

# Deep Stream Colors
CYAN = "#00f2ff"
VIOLET = "#7000ff"
DARK_BG = "#0a0e27"
LIGHT_TEXT = "#e0e0e0"

THEME = {
    "primary": CYAN,
    "secondary": VIOLET,
    "bg": DARK_BG,
    "text": LIGHT_TEXT,
    "accent": "#00ff88",
    "error": "#ff0055",
}

console = Console()


def render_header(title: str, subtitle: str = "") -> None:
    """Render a beautiful header with Deep Stream styling."""
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
        footer_text.append(f" • {provider}", style=f"dim {CYAN}")
    console.print(footer_text)


def render_divider() -> None:
    """Render a styled divider."""
    console.print(Text("─" * 80, style=f"dim {VIOLET}"))
