"""Exit summary with split-flap odometer animation.

Shows session stats in a bordered box, then animates the total token
count digit-by-digit from 0 to target.
"""

import sys
import threading
import time

from rich.console import Console
from rich.live import Live
from rich.text import Text

from .theme import DEFAULT_THEME, PROVIDER_THEMES

_TOP_LEFT = "\u256d"
_TOP_RIGHT = "\u256e"
_BOT_LEFT = "\u2570"
_BOT_RIGHT = "\u256f"
_VERT = "\u2502"
_HORIZ = "\u2500"


def render_exit_summary(
    session_id: str,
    messages: int,
    responses: int,
    input_tokens: int,
    output_tokens: int,
    wall_time: str,
    provider: str,
    model: str,
    provider_tokens: dict[str, int] | None = None,
    console: Console | None = None,
    animate: bool = True,
) -> None:
    """Render the bordered exit summary with optional odometer animation.

    Args:
        session_id: Short session identifier.
        messages: User message count.
        responses: Assistant response count.
        input_tokens: Total input tokens.
        output_tokens: Total output tokens.
        wall_time: Formatted wall time string.
        provider: Current provider name.
        model: Current model name.
        provider_tokens: Per-provider token usage for colored display.
        console: Rich Console.
        animate: Whether to play the odometer animation.
    """
    from .theme import console as default_console

    con = console or default_console
    palette = DEFAULT_THEME.palette
    width = min(con.width or 60, 60)
    inner = width - 4

    con.print()

    # Top border
    top = Text()
    label = " session summary "
    fill = inner - len(label)
    left_fill = fill // 2
    right_fill = fill - left_fill
    top.append(_TOP_LEFT, style=f"dim {palette.border}")
    top.append(_HORIZ * left_fill, style=f"dim {palette.border}")
    top.append(label, style=f"dim {palette.text_dim}")
    top.append(_HORIZ * right_fill, style=f"dim {palette.border}")
    top.append(_TOP_RIGHT, style=f"dim {palette.border}")
    con.print(top)

    # Content lines
    total = input_tokens + output_tokens
    lines = [
        ("session", session_id),
        ("messages", f"{messages} sent / {responses} received"),
        ("tokens", f"{_fmt(input_tokens)} in / {_fmt(output_tokens)} out"),
        ("time", wall_time),
        ("provider", f"{provider} ({model})"),
    ]

    for key, value in lines:
        row = Text()
        row.append(f"{_VERT}  ", style=f"dim {palette.border}")
        row.append(f"{key:<12}", style=f"dim {palette.text_dim}")
        row.append(value, style=palette.text)
        # Pad to inner width
        pad = inner - len(key) - len(value) - 12 + 10
        row.append(" " * max(pad, 0))
        row.append(f"  {_VERT}", style=f"dim {palette.border}")
        con.print(row)

    # Provider token breakdown
    if provider_tokens:
        row = Text()
        row.append(f"{_VERT}  ", style=f"dim {palette.border}")
        row.append(f"{'usage':<12}", style=f"dim {palette.text_dim}")
        for name, theme in PROVIDER_THEMES.items():
            count = provider_tokens.get(name, 0)
            if count > 0:
                row.append(f"{theme.abbreviation}:", style=f"dim {palette.text_dim}")
                row.append(f"{_fmt(count)} ", style=f"{theme.accent}")
        con.print(row)

    # Bottom border
    bot = Text()
    bot.append(_BOT_LEFT, style=f"dim {palette.border}")
    bot.append(_HORIZ * (inner + 2), style=f"dim {palette.border}")
    bot.append(_BOT_RIGHT, style=f"dim {palette.border}")
    con.print(bot)

    # Odometer animation
    if animate and total > 0:
        _animate_odometer(total, con)

    con.print()


def _animate_odometer(target: int, console: Console) -> None:
    """Animate a 10-digit split-flap counter from 0 to target."""
    palette = DEFAULT_THEME.palette
    digits_str = f"{target:>10d}"
    target_digits = [int(d) if d != " " else 0 for d in digits_str]

    # Track if user wants to skip
    skip = threading.Event()

    def _listen_skip():
        """Listen for any keypress to skip animation."""
        try:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while not skip.is_set():
                    if sys.stdin.readable():
                        sys.stdin.read(1)
                        skip.set()
                        break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass

    listener = threading.Thread(target=_listen_skip, daemon=True)
    listener.start()

    current = [0] * 10

    try:
        with Live(console=console, refresh_per_second=30, transient=True) as live:
            # Animate each digit position from right to left
            for pos in range(9, -1, -1):
                if skip.is_set():
                    break
                tgt = target_digits[pos]
                while current[pos] != tgt:
                    if skip.is_set():
                        break
                    current[pos] = (current[pos] + 1) % 10
                    display = _render_digits(current, palette)
                    live.update(display)
                    time.sleep(0.03)

            # Final display
            for i in range(10):
                current[i] = target_digits[i]
            live.update(_render_digits(current, palette))
    except Exception:
        pass
    finally:
        skip.set()


def _render_digits(digits: list[int], palette) -> Text:
    """Render the odometer digit display."""
    t = Text()
    t.append("  total: ", style=f"dim {palette.text_dim}")
    for d in digits:
        t.append(str(d), style=f"bold {palette.text_bright}")
    t.append(" tokens", style=f"dim {palette.text_dim}")
    return t


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)
