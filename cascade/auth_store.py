"""Token persistence for Cascade auth flows.

Stores provider tokens in ~/.config/cascade/tokens/{provider}.json.
All credential sources (CLI detection, OAuth, API key paste) funnel here.
"""

import json
import time
from pathlib import Path
from typing import Optional, Any


_TOKENS_DIR = Path("~/.config/cascade/tokens").expanduser()


class TokenStore:
    """Read/write provider tokens to ~/.config/cascade/tokens/."""

    def __init__(self, base_dir: Optional[Path] = None):
        self._dir = base_dir or _TOKENS_DIR

    def _path(self, provider: str) -> Path:
        return self._dir / f"{provider}.json"

    def save(self, provider: str, token_data: dict[str, Any]) -> None:
        """Save token data for a provider."""
        self._dir.mkdir(parents=True, exist_ok=True)
        token_data = {**token_data, "saved_at": time.time()}
        self._path(provider).write_text(
            json.dumps(token_data, indent=2), encoding="utf-8"
        )

    def load(self, provider: str) -> Optional[dict[str, Any]]:
        """Load token data for a provider. Returns None if not found."""
        path = self._path(provider)
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def is_expired(self, provider: str) -> bool:
        """Check if the stored token is expired.

        Returns True if expired or no token exists.
        """
        data = self.load(provider)
        if data is None:
            return True

        expires_in = data.get("expires_in")
        saved_at = data.get("saved_at")

        if expires_in is None or saved_at is None:
            # No expiry info -- assume valid (e.g. API keys)
            return False

        return time.time() > (saved_at + expires_in)

    def clear(self, provider: str) -> None:
        """Remove stored token for a provider."""
        path = self._path(provider)
        if path.exists():
            path.unlink()

    def list_providers(self) -> list[str]:
        """List providers with stored tokens."""
        if not self._dir.is_dir():
            return []
        return [
            p.stem for p in self._dir.glob("*.json")
        ]
