"""Exit summary screen with odometer animation.

Centered bordered card on cleared background.
Shows session stats, per-provider token breakdown, odometer total.
Any key dismisses and exits the application.
"""

from rich.text import Text
from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.widgets import Static
from textual.binding import Binding

from ..widgets.odometer import OdometerCounter
from ..widgets.status_bar import StatusBar
from ..theme import PALETTE, PROVIDERS, get_accent


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


class ExitScreen(Screen):
    """Session summary shown before exiting."""

    BINDINGS = [
        Binding("any", "dismiss_exit", "Exit", show=False),
    ]

    def __init__(
        self,
        session_id: str,
        uptime: str,
        messages_sent: int,
        messages_received: int,
        tokens: dict[str, int],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._session_id = session_id
        self._uptime = uptime
        self._sent = messages_sent
        self._received = messages_received
        self._tokens = tokens
        self._total = sum(tokens.values())

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield SessionEndCard(
                    session_id=self._session_id,
                    uptime=self._uptime,
                    messages_sent=self._sent,
                    messages_received=self._received,
                    tokens=self._tokens,
                    total_tokens=self._total,
                )
        yield _ExitStatusBar()

    def on_key(self, event) -> None:
        # Skip animation on first key, exit on second
        try:
            odo = self.query_one(OdometerCounter)
            if odo._animating:
                odo.skip_animation()
                return
        except Exception:
            pass
        self.app.exit()

    def action_dismiss_exit(self) -> None:
        self.app.exit()


class _ExitStatusBar(Static):
    """Status bar override for exit screen."""

    DEFAULT_CSS = """
    _ExitStatusBar {
        dock: bottom;
        height: 1;
        width: 100%;
        background: #121218;
        padding: 0 2;
    }
    """

    def render(self) -> Text:
        return Text(" session closed", style=f"dim {PALETTE.text_dim}")


class SessionEndCard(Static):
    """Bordered card with session stats and odometer."""

    DEFAULT_CSS = """
    SessionEndCard {
        width: 62;
        height: auto;
        border: round #30363d;
        background: #121218;
        padding: 1 4;
    }
    """

    def __init__(
        self,
        session_id: str,
        uptime: str,
        messages_sent: int,
        messages_received: int,
        tokens: dict[str, int],
        total_tokens: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._session_id = session_id
        self._uptime = uptime
        self._sent = messages_sent
        self._received = messages_received
        self._tokens = tokens
        self._total = total_tokens

    def compose(self) -> ComposeResult:
        # Title
        yield _CardRow("", "SESSION ENDED", bold=True, center=True)
        yield Static("")

        # Stats rows
        yield _CardRow("SESSION", self._session_id)
        yield _CardRow("UPTIME", self._uptime)
        yield _CardRow("MESSAGES", f"{self._sent} sent . {self._received} received")
        yield Static("")

        # Provider breakdown
        yield ProviderSummaryLine(self._tokens)
        yield Static("")

        # Odometer
        yield _CardRow("TOTAL", "")
        yield OdometerCounter(self._total)
        yield Static("")

        # Footer
        yield _CardRow("", "press any key . session saved to history", dim=True, center=True)


class _CardRow(Static):
    """A single label: value row in the exit card."""

    def __init__(
        self,
        label: str,
        value: str,
        bold: bool = False,
        dim: bool = False,
        center: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._bold = bold
        self._dim = dim
        self._center = center

    def render(self) -> Text:
        t = Text()
        if self._center:
            style = f"bold {PALETTE.text_bright}" if self._bold else f"dim {PALETTE.text_dim}"
            t.append(self._value, style=style)
            return t

        if self._label:
            t.append(f"{self._label:<12}", style=f"dim {PALETTE.text_dim}")
        t.append(self._value, style=PALETTE.text_primary)
        return t


class ProviderSummaryLine(Static):
    """Colored per-provider token summary."""

    def __init__(self, tokens: dict[str, int], **kwargs) -> None:
        super().__init__(**kwargs)
        self._tokens = tokens

    def render(self) -> Text:
        t = Text()
        t.append(f"{'PROVIDERS':<12}", style=f"dim {PALETTE.text_dim}")
        parts = []
        for name, count in self._tokens.items():
            if count > 0:
                accent = get_accent(name)
                part = Text()
                part.append(name, style=f"bold {accent}")
                part.append(f" {_fmt(count)}", style=f"dim {PALETTE.text_dim}")
                parts.append(part)

        for i, part in enumerate(parts):
            t.append_text(part)
            if i < len(parts) - 1:
                t.append(" . ", style=f"dim {PALETTE.text_dim}")

        return t
