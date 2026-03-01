"""Interactive authentication flows for Cascade providers.

Supports:
- Google/Gemini: Full OAuth2 device-code flow
- Anthropic/Claude: CLI credential detection + API key fallback
- OpenAI: CLI credential detection + API key fallback
- OpenRouter: API key entry

Each flow returns an AuthResult or None on cancellation.
"""

import json
import os
import shutil
import time
import webbrowser
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError

from .auth import detect_claude, detect_codex, detect_gemini
from .auth_store import TokenStore
from .ui.theme import console, CYAN, VIOLET


# Google OAuth2 device-code flow credentials.
# Keep defaults non-sensitive; callers can override through environment.
_GOOGLE_CLIENT_ID = os.getenv("CASCADE_GOOGLE_CLIENT_ID", "cascade-public-client-id")
_GOOGLE_CLIENT_SECRET = os.getenv(
    "CASCADE_GOOGLE_CLIENT_SECRET", "cascade-public-client-secret",
)
_GOOGLE_SCOPES = "https://www.googleapis.com/auth/cloud-platform openid email profile"
_GOOGLE_DEVICE_URL = "https://oauth2.googleapis.com/device/code"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

_store = TokenStore()


@dataclass(frozen=True)
class AuthResult:
    """Result of an authentication flow."""
    provider: str
    token: str
    email: str
    method: str  # "oauth", "cli_detected", "api_key"


def login(provider: str) -> Optional[AuthResult]:
    """Interactive login for a single provider.

    Dispatches to the provider-specific strategy.
    """
    handlers = {
        "gemini": login_google,
        "google": login_google,
        "claude": login_anthropic,
        "anthropic": login_anthropic,
        "openai": login_openai,
        "openrouter": login_openrouter,
    }

    handler = handlers.get(provider.lower())
    if handler is None:
        console.print(f"Unknown provider: {provider}", style="dim red")
        console.print(
            f"Available: {', '.join(sorted(set(handlers.values().__class__.__name__ for _ in [0])))}"
            f" gemini, claude, openai, openrouter",
            style="dim",
        )
        return None

    return handler()


def show_auth_status() -> None:
    """Display authentication status for all providers."""
    console.print("\n  Auth Status:", style=f"bold {CYAN}")

    providers_status = [
        ("gemini", detect_gemini, "Gemini CLI"),
        ("claude", detect_claude, "Claude CLI"),
        ("openai", detect_codex, "Codex CLI"),
    ]

    for name, detect_fn, cli_name in providers_status:
        stored = _store.load(name)
        cli_cred = detect_fn()
        expired = _store.is_expired(name)

        if stored and not expired:
            method = stored.get("method", "unknown")
            console.print(f"    {name:<12} authenticated ({method})", style="green")
        elif cli_cred:
            label = cli_cred.source
            if cli_cred.email:
                label += f" ({cli_cred.email})"
            console.print(f"    {name:<12} {label}", style="green")
        else:
            console.print(f"    {name:<12} not configured", style="dim")

    # OpenRouter (API key only, check store)
    stored = _store.load("openrouter")
    if stored:
        console.print(f"    {'openrouter':<12} authenticated (api_key)", style="green")
    else:
        console.print(f"    {'openrouter':<12} not configured", style="dim")

    console.print()
    console.print("  Use /login <provider> to authenticate.", style="dim")
    console.print()


def login_google() -> Optional[AuthResult]:
    """Google OAuth2 device-code flow using public Gemini CLI credentials."""
    # Check for existing CLI credentials first
    cred = detect_gemini()
    if cred:
        console.print("  Gemini CLI credentials detected.", style=f"dim {CYAN}")
        answer = _prompt("  Use existing credentials? [Y/n]: ", default="y")
        if answer.lower() in ("y", "yes", ""):
            _store.save("gemini", {
                "access_token": cred.token,
                "method": "cli_detected",
                "email": cred.email,
            })
            return AuthResult(
                provider="gemini",
                token=cred.token,
                email=cred.email,
                method="cli_detected",
            )

    # Device code flow
    console.print("\n  Starting Google OAuth2 device authorization...\n", style=f"dim {CYAN}")

    try:
        device_data = _google_device_code_request()
    except Exception as exc:
        console.print(f"  Failed to initiate device flow: {exc}", style="dim red")
        return _fallback_api_key("gemini")

    user_code = device_data.get("user_code", "")
    verification_url = device_data.get("verification_url", "")
    device_code = device_data.get("device_code", "")
    interval = device_data.get("interval", 5)
    expires_in = device_data.get("expires_in", 300)

    console.print(f"  Visit: {verification_url}", style=f"bold {VIOLET}")
    console.print(f"  Enter code: {user_code}\n", style=f"bold {CYAN}")

    try:
        webbrowser.open(verification_url)
    except Exception:
        pass

    console.print("  Waiting for authorization...", style="dim")

    token_data = _google_poll_token(device_code, interval, expires_in)
    if token_data is None:
        console.print("  Authorization timed out or was denied.", style="dim red")
        return _fallback_api_key("gemini")

    # Extract email from id_token if present
    email = ""
    id_token = token_data.get("id_token", "")
    if id_token:
        from .auth import _decode_jwt_payload
        payload = _decode_jwt_payload(id_token)
        email = payload.get("email", "")

    # Save to store
    _store.save("gemini", {
        **token_data,
        "method": "oauth",
        "email": email,
    })

    access_token = token_data.get("access_token", "")
    console.print(f"  Authenticated as {email or 'Google user'}.", style=f"dim {CYAN}")

    return AuthResult(
        provider="gemini",
        token=access_token,
        email=email,
        method="oauth",
    )


def login_anthropic() -> Optional[AuthResult]:
    """Anthropic auth: detect CLI, guide CLI login, or accept API key."""
    # Check CLI credentials
    cred = detect_claude()
    if cred:
        label = "Claude Code CLI"
        if cred.plan:
            label += f" [{cred.plan}]"
        console.print(f"  {label} credentials detected.", style=f"dim {CYAN}")
        answer = _prompt("  Use existing credentials? [Y/n]: ", default="y")
        if answer.lower() in ("y", "yes", ""):
            _store.save("claude", {
                "access_token": cred.token,
                "method": "cli_detected",
                "plan": cred.plan,
            })
            return AuthResult(
                provider="claude",
                token=cred.token,
                email=cred.email,
                method="cli_detected",
            )

    # Check if claude CLI is installed
    if shutil.which("claude"):
        console.print(
            "  Claude CLI is installed. Run 'claude login' to authenticate,\n"
            "  then try /login claude again.",
            style="dim",
        )
        return None

    return _fallback_api_key("claude", url="https://console.anthropic.com/settings/keys")


def login_openai() -> Optional[AuthResult]:
    """OpenAI auth: detect CLI, guide CLI login, or accept API key."""
    cred = detect_codex()
    if cred:
        label = "Codex CLI"
        if cred.email:
            label += f" ({cred.email})"
        if cred.plan:
            label += f" [{cred.plan}]"
        console.print(f"  {label} credentials detected.", style=f"dim {CYAN}")
        answer = _prompt("  Use existing credentials? [Y/n]: ", default="y")
        if answer.lower() in ("y", "yes", ""):
            _store.save("openai", {
                "access_token": cred.token,
                "method": "cli_detected",
                "email": cred.email,
            })
            return AuthResult(
                provider="openai",
                token=cred.token,
                email=cred.email,
                method="cli_detected",
            )

    if shutil.which("codex"):
        console.print(
            "  Codex CLI is installed. Run 'codex login' to authenticate,\n"
            "  then try /login openai again.",
            style="dim",
        )
        return None

    return _fallback_api_key("openai", url="https://platform.openai.com/api-keys")


def login_openrouter() -> Optional[AuthResult]:
    """OpenRouter: API key only."""
    return _fallback_api_key("openrouter", url="https://openrouter.ai/keys")


# --- Internal helpers ---


def _prompt(message: str, default: str = "") -> str:
    """Read user input with a default."""
    try:
        value = input(message)
        return value if value else default
    except (EOFError, KeyboardInterrupt):
        return default


def _fallback_api_key(
    provider: str, url: str = ""
) -> Optional[AuthResult]:
    """Prompt the user to paste an API key."""
    if url:
        console.print(f"\n  Get your API key from: {url}", style="dim")
        try:
            webbrowser.open(url)
        except Exception:
            pass

    key = _prompt(f"  Paste {provider} API key (or Enter to cancel): ")
    if not key:
        return None

    _store.save(provider, {
        "access_token": key,
        "method": "api_key",
    })

    return AuthResult(
        provider=provider,
        token=key,
        email="",
        method="api_key",
    )


def _google_device_code_request() -> dict:
    """Request a device code from Google OAuth2."""
    data = urlencode({
        "client_id": _GOOGLE_CLIENT_ID,
        "scope": _GOOGLE_SCOPES,
    }).encode()

    req = Request(_GOOGLE_DEVICE_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _google_poll_token(
    device_code: str, interval: int, expires_in: int
) -> Optional[dict]:
    """Poll Google's token endpoint until authorized or timeout."""
    deadline = time.time() + expires_in
    data = urlencode({
        "client_id": _GOOGLE_CLIENT_ID,
        "client_secret": _GOOGLE_CLIENT_SECRET,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }).encode()

    while time.time() < deadline:
        time.sleep(interval)

        req = Request(_GOOGLE_TOKEN_URL, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urlopen(req, timeout=15) as resp:
                token_data = json.loads(resp.read())
                if "access_token" in token_data:
                    return token_data
        except URLError as exc:
            # HTTP errors come through here; check for "authorization_pending"
            body = ""
            if hasattr(exc, "read"):
                try:
                    body = exc.read().decode()
                except Exception:
                    pass
            elif hasattr(exc, "reason"):
                body = str(exc.reason)

            if "authorization_pending" in body:
                continue
            if "slow_down" in body:
                interval += 1
                continue
            # Unexpected error
            break

    return None
