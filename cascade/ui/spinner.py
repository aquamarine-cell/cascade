"""Gutter-aligned thinking spinner with braille animation."""

import sys
import threading
import time

from .gutter import GUTTER_WIDTH
from .theme import DEFAULT_THEME

_FRAMES = list("\u280b\u2819\u2839\u2838\u283c\u2834\u2826\u2827\u2807\u280f")


class GutterSpinner:
    """Braille spinner that renders in the gutter position.

    Usage:
        spinner = GutterSpinner("cla", "#f0956c")
        spinner.start()
        # ... wait for first token ...
        spinner.stop()
    """

    def __init__(self, abbreviation: str, accent: str, label: str = "thinking..."):
        self._abbr = abbreviation
        self._accent = accent
        self._label = label
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None
        # Clear the spinner line
        sys.stderr.write(f"\r{' ' * (GUTTER_WIDTH + len(self._label) + 10)}\r")
        sys.stderr.flush()

    def _spin(self) -> None:
        palette = DEFAULT_THEME.palette
        idx = 0
        while self._running:
            frame = _FRAMES[idx % len(_FRAMES)]
            # ANSI escape for color: use amber for spinner char
            line = f"\r{self._abbr:<4}\x1b[2m| \x1b[0m\x1b[38;2;229;199;71m{frame}\x1b[0m \x1b[2m{self._label}\x1b[0m"
            sys.stderr.write(line)
            sys.stderr.flush()
            idx += 1
            time.sleep(0.08)
