"""Detect credentials from installed CLI tools.

Reads authentication tokens from:
  - Claude Code:  ~/.claude/.credentials.json
  - Gemini CLI:   ~/.gemini/oauth_creds.json
  - Codex CLI:    ~/.codex/auth.json

These are the same credentials the user already authenticated with
when setting up those CLI tools.
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DetectedCredential:
    """A credential discovered from an installed CLI tool."""
    provider: str
    source: str
    token: str
    email: str
    plan: str


def _read_json(path: Path) -> Optional[dict]:
    """Read a JSON file, returning None on any failure."""
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _decode_jwt_payload(token: str) -> dict:
    """Decode the payload of a JWT without verification (for reading email/plan)."""
    import base64
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        # Add padding
        payload += "=" * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception:
        return {}


def detect_claude() -> Optional[DetectedCredential]:
    """Detect Claude Code OAuth credentials."""
    data = _read_json(Path.home() / ".claude" / ".credentials.json")
    if data is None:
        return None
    oauth = data.get("claudeAiOauth", {})
    token = oauth.get("accessToken", "")
    if not token:
        return None
    plan = oauth.get("subscriptionType", "unknown")
    return DetectedCredential(
        provider="claude",
        source="Claude Code CLI",
        token=token,
        email="",
        plan=plan,
    )


def detect_gemini() -> Optional[DetectedCredential]:
    """Detect Gemini CLI OAuth credentials."""
    data = _read_json(Path.home() / ".gemini" / "oauth_creds.json")
    if data is None:
        return None
    token = data.get("access_token", "")
    if not token:
        return None
    expiry_date = data.get("expiry_date")
    if isinstance(expiry_date, (int, float)):
        # Gemini stores expiry_date as epoch milliseconds.
        now_ms = int(time.time() * 1000)
        # Add a one-minute skew so near-expired tokens are treated as expired.
        if now_ms >= int(expiry_date) - 60_000:
            return None
    # Extract email from id_token JWT
    email = ""
    id_token = data.get("id_token", "")
    if id_token:
        payload = _decode_jwt_payload(id_token)
        email = payload.get("email", "")
    return DetectedCredential(
        provider="gemini",
        source="Gemini CLI",
        token=token,
        email=email,
        plan="Google One AI Pro",
    )


def detect_codex() -> Optional[DetectedCredential]:
    """Detect OpenAI Codex CLI credentials."""
    data = _read_json(Path.home() / ".codex" / "auth.json")
    if data is None:
        return None
    tokens = data.get("tokens", {})
    access_token = tokens.get("access_token", "")
    if not access_token:
        return None
    # Extract email and plan from id_token or access_token JWT
    email = ""
    plan = ""
    id_token = tokens.get("id_token", "")
    if id_token:
        payload = _decode_jwt_payload(id_token)
        email = payload.get("email", "")
        auth_info = payload.get("https://api.openai.com/auth", {})
        plan = auth_info.get("chatgpt_plan_type", "")
    return DetectedCredential(
        provider="openai",
        source="Codex CLI",
        token=access_token,
        email=email,
        plan=plan,
    )


def detect_all() -> list[DetectedCredential]:
    """Detect all available CLI credentials.

    Checks TokenStore first (our own saved tokens), then CLI credential files.
    Prefers the freshest token when both exist.
    """
    found = []
    seen_providers: set[str] = set()

    # Check TokenStore first
    try:
        from .auth_store import TokenStore
        store = TokenStore()
        for provider in store.list_providers():
            if store.is_expired(provider):
                continue
            data = store.load(provider)
            if data and data.get("access_token"):
                found.append(DetectedCredential(
                    provider=provider,
                    source=f"Cascade ({data.get('method', 'saved')})",
                    token=data["access_token"],
                    email=data.get("email", ""),
                    plan=data.get("plan", ""),
                ))
                seen_providers.add(provider)
    except Exception:
        pass

    # Then check CLI credential files for providers not yet found
    for detector in (detect_claude, detect_gemini, detect_codex):
        cred = detector()
        if cred is not None and cred.provider not in seen_providers:
            found.append(cred)
    return found


def format_auth_summary(credentials: list[DetectedCredential]) -> str:
    """Format a one-line summary of detected auth for the banner."""
    if not credentials:
        return ""
    parts = []
    for cred in credentials:
        label = cred.source
        if cred.email:
            label += f" ({cred.email})"
        if cred.plan:
            label += f" [{cred.plan}]"
        parts.append(label)
    return "Logged in: " + ", ".join(parts)
