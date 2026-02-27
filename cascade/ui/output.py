"""Output rendering functions."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.syntax import Syntax
from typing import Iterator, Optional
import sys

from .theme import CYAN, VIOLET, LIGHT_TEXT, console

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def render_response(
    text: str,
    provider: str = "",
    thinking: str = "",
    language: str = "text",
) -> None:
    """Render a complete response."""
    if thinking:
        thinking_panel = Panel(
            Text(thinking, style=f"dim {LIGHT_TEXT}"),
            title=Text("💭 Thinking", style=VIOLET),
            border_style=VIOLET,
            padding=(1, 2),
        )
        console.print(thinking_panel)
    
    # Syntax highlight if it looks like code
    if language != "text" or (text.startswith("```") or text.startswith("def ") or text.startswith("import ")):
        try:
            syntax = Syntax(
                text,
                language or "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
            )
            panel = Panel(
                syntax,
                title=Text(f"📝 {provider}", style=CYAN) if provider else None,
                border_style=CYAN,
                padding=(1, 2),
            )
            console.print(panel)
        except:
            # Fall back to plain text
            panel = Panel(
                Text(text, style=LIGHT_TEXT),
                title=Text(f"📝 {provider}", style=CYAN) if provider else None,
                border_style=CYAN,
                padding=(1, 2),
            )
            console.print(panel)
    else:
        panel = Panel(
            Text(text, style=LIGHT_TEXT),
            title=Text(f"📝 {provider}", style=CYAN) if provider else None,
            border_style=CYAN,
            padding=(1, 2),
        )
        console.print(panel)


def stream_response(
    stream_iter: Iterator[str],
    provider: str = "",
) -> str:
    """Stream and display response in real-time."""
    console.print(Text(f"▶ Streaming from {provider}...", style=f"dim {CYAN}"))
    
    full_text = ""
    for i, chunk in enumerate(stream_iter):
        full_text += chunk
        # Live update without newlines for smooth streaming
        sys.stdout.write(chunk)
        sys.stdout.flush()
    
    console.print()  # New line after streaming
    return full_text


def render_comparison(results: list[dict]) -> None:
    """Render side-by-side comparison of multiple providers."""
    panels = []
    for result in results:
        provider = result.get("provider", "Unknown")
        response = result.get("response", "")
        
        # Truncate for display
        display_text = response[:500] + "..." if len(response) > 500 else response
        
        panel = Panel(
            Text(display_text, style=LIGHT_TEXT),
            title=Text(f"🔷 {provider}", style=CYAN),
            border_style=CYAN,
            padding=(1, 2),
        )
        panels.append(panel)
    
    # Display side by side if possible
    if len(panels) <= 2:
        if len(panels) == 2:
            cols = Columns(panels, equal=True, expand=True)
            console.print(cols)
        else:
            console.print(panels[0])
    else:
        for panel in panels:
            console.print(panel)


def render_thinking(text: str) -> None:
    """Render thinking/processing output."""
    panel = Panel(
        Text(text, style=f"dim {LIGHT_TEXT}"),
        title=Text("💭 Analyzing", style=VIOLET),
        border_style=VIOLET,
        padding=(1, 2),
    )
    console.print(panel)


def render_error(text: str) -> None:
    """Render error message."""
    panel = Panel(
        Text(text, style="bold #ff0055"),
        title=Text("❌ Error", style="#ff0055"),
        border_style="#ff0055",
        padding=(1, 2),
    )
    console.print(panel)
