"""Output rendering -- thin facade over gutter, code_block, and stream modules.

Preserves backward-compatible function signatures used by cli.py.
"""

from typing import Iterator

from rich.text import Text

from .stream import StreamRenderer
from .theme import DEFAULT_THEME, console


def render_response(
    text: str,
    provider: str = "",
    thinking: str = "",
    language: str = "text",
) -> None:
    """Render a complete response through the gutter system."""
    theme = DEFAULT_THEME.get_provider(provider)

    if thinking:
        palette = DEFAULT_THEME.palette
        think_line = Text()
        think_line.append("[thinking] ", style=f"dim {palette.text_dim}")
        think_line.append(thinking[:200], style=f"dim {palette.text}")
        console.print(think_line)

    # Use the stream renderer for consistent handling of code blocks
    renderer = StreamRenderer(theme, console)
    renderer.feed(text)
    renderer.finish()


def stream_response(
    stream_iter: Iterator[str],
    provider: str = "",
) -> str:
    """Stream and display response in real-time through the gutter."""
    theme = DEFAULT_THEME.get_provider(provider)
    renderer = StreamRenderer(theme, console)

    full_text = ""
    for chunk in stream_iter:
        full_text += chunk
        renderer.feed(chunk)

    renderer.finish()
    return full_text


def render_error(text: str) -> None:
    """Render an error message."""
    palette = DEFAULT_THEME.palette
    err = Text()
    err.append("err ", style=f"bold {palette.error}")
    err.append("| ", style=f"dim {palette.text_muted}")
    err.append(text, style=palette.error)
    console.print(err)


def render_comparison(results: list[dict]) -> None:
    """Render comparison results from multiple providers."""
    for result in results:
        provider = result.get("provider", "unknown")
        response = result.get("response", "")
        theme = DEFAULT_THEME.get_provider(provider)

        # Render header line
        header = Text()
        header.append(f"{theme.abbreviation} ", style=f"bold {theme.accent}")
        header.append("| ", style=f"dim {DEFAULT_THEME.palette.text_muted}")
        header.append(f"[{provider}]", style=f"dim {DEFAULT_THEME.palette.text_dim}")
        console.print(header)

        # Render response body
        renderer = StreamRenderer(theme, console)
        renderer._first_line = False  # header already printed
        renderer.feed(response)
        renderer.finish()
        console.print()


def render_thinking(text: str) -> None:
    """Render thinking/processing output."""
    palette = DEFAULT_THEME.palette
    t = Text()
    t.append("... ", style=f"dim {palette.spinner}")
    t.append("| ", style=f"dim {palette.text_muted}")
    t.append(text, style=f"dim {palette.text}")
    console.print(t)
