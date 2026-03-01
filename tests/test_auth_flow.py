"""Tests for auth flow and token store modules."""

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from cascade.auth import DetectedCredential
from cascade.auth_store import TokenStore
from cascade.auth_flow import (
    AuthResult,
    login,
    login_google,
    login_anthropic,
    login_openai,
    login_openrouter,
)


# --- TokenStore tests ---


class TestTokenStore:
    def test_save_and_load(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        store.save("gemini", {"access_token": "tok123", "email": "a@b.com"})
        data = store.load("gemini")
        assert data["access_token"] == "tok123"
        assert data["email"] == "a@b.com"
        assert "saved_at" in data

    def test_load_missing(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        assert store.load("nonexistent") is None

    def test_is_expired_no_token(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        assert store.is_expired("gemini") is True

    def test_is_expired_no_expiry_info(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        store.save("gemini", {"access_token": "tok"})
        # No expires_in -> assumed valid
        assert store.is_expired("gemini") is False

    def test_is_expired_fresh_token(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        store.save("gemini", {"access_token": "tok", "expires_in": 3600})
        assert store.is_expired("gemini") is False

    def test_is_expired_old_token(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        # Save with a past saved_at
        data = {"access_token": "tok", "expires_in": 10, "saved_at": time.time() - 100}
        (tmp_path / "gemini.json").write_text(json.dumps(data))
        assert store.is_expired("gemini") is True

    def test_clear(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        store.save("gemini", {"access_token": "tok"})
        store.clear("gemini")
        assert store.load("gemini") is None

    def test_list_providers(self, tmp_path):
        store = TokenStore(base_dir=tmp_path)
        store.save("gemini", {"token": "a"})
        store.save("claude", {"token": "b"})
        providers = store.list_providers()
        assert sorted(providers) == ["claude", "gemini"]


# --- Login dispatcher ---


class TestLoginDispatcher:
    @patch("cascade.auth_flow.login_google")
    def test_routes_gemini(self, mock_login):
        mock_login.return_value = AuthResult("gemini", "tok", "", "oauth")
        result = login("gemini")
        mock_login.assert_called_once()
        assert result.provider == "gemini"

    @patch("cascade.auth_flow.login_anthropic")
    def test_routes_claude(self, mock_login):
        mock_login.return_value = AuthResult("claude", "tok", "", "cli_detected")
        result = login("claude")
        mock_login.assert_called_once()

    def test_unknown_provider(self):
        result = login("nonexistent_provider")
        assert result is None


# --- Google OAuth flow ---


class TestGoogleLogin:
    @patch("cascade.auth_flow._prompt")
    @patch("cascade.auth_flow.detect_gemini")
    @patch("cascade.auth_flow._store")
    def test_uses_existing_cli_creds(self, mock_store, mock_detect, mock_prompt):
        mock_detect.return_value = DetectedCredential(
            provider="gemini",
            source="Gemini CLI",
            token="existing-token",
            email="user@gmail.com",
            plan="Google One AI Pro",
        )
        mock_prompt.return_value = "y"

        result = login_google()

        assert result is not None
        assert result.provider == "gemini"
        assert result.token == "existing-token"
        assert result.method == "cli_detected"
        mock_store.save.assert_called_once()

    @patch("cascade.auth_flow.webbrowser")
    @patch("cascade.auth_flow._google_poll_token")
    @patch("cascade.auth_flow._google_device_code_request")
    @patch("cascade.auth_flow.detect_gemini")
    @patch("cascade.auth_flow._store")
    def test_device_code_flow(
        self, mock_store, mock_detect, mock_device, mock_poll, mock_browser
    ):
        mock_detect.return_value = None
        mock_device.return_value = {
            "device_code": "dev123",
            "user_code": "ABCD-1234",
            "verification_url": "https://google.com/device",
            "interval": 1,
            "expires_in": 60,
        }
        mock_poll.return_value = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh",
            "id_token": "",
            "expires_in": 3600,
        }

        result = login_google()

        assert result is not None
        assert result.provider == "gemini"
        assert result.token == "new-access-token"
        assert result.method == "oauth"


# --- Anthropic login ---


class TestAnthropicLogin:
    @patch("cascade.auth_flow._prompt")
    @patch("cascade.auth_flow.detect_claude")
    @patch("cascade.auth_flow._store")
    def test_uses_existing_cli_creds(self, mock_store, mock_detect, mock_prompt):
        mock_detect.return_value = DetectedCredential(
            provider="claude",
            source="Claude Code CLI",
            token="claude-token",
            email="",
            plan="max_5x",
        )
        mock_prompt.return_value = "y"

        result = login_anthropic()

        assert result is not None
        assert result.provider == "claude"
        assert result.method == "cli_detected"

    @patch("cascade.auth_flow.webbrowser")
    @patch("cascade.auth_flow._prompt")
    @patch("cascade.auth_flow.shutil")
    @patch("cascade.auth_flow.detect_claude")
    @patch("cascade.auth_flow._store")
    def test_fallback_to_api_key(
        self, mock_store, mock_detect, mock_shutil, mock_prompt, mock_browser
    ):
        mock_detect.return_value = None
        mock_shutil.which.return_value = None
        mock_prompt.return_value = "sk-ant-api-key-123"

        result = login_anthropic()

        assert result is not None
        assert result.method == "api_key"
        assert result.token == "sk-ant-api-key-123"


# --- OpenAI login ---


class TestOpenAILogin:
    @patch("cascade.auth_flow._prompt")
    @patch("cascade.auth_flow.detect_codex")
    @patch("cascade.auth_flow._store")
    def test_uses_existing_cli_creds(self, mock_store, mock_detect, mock_prompt):
        mock_detect.return_value = DetectedCredential(
            provider="openai",
            source="Codex CLI",
            token="openai-token",
            email="user@openai.com",
            plan="plus",
        )
        mock_prompt.return_value = "y"

        result = login_openai()

        assert result is not None
        assert result.provider == "openai"
        assert result.method == "cli_detected"


# --- OpenRouter login ---


class TestOpenRouterLogin:
    @patch("cascade.auth_flow.webbrowser")
    @patch("cascade.auth_flow._prompt")
    @patch("cascade.auth_flow._store")
    def test_api_key_entry(self, mock_store, mock_prompt, mock_browser):
        mock_prompt.return_value = "sk-or-key-123"

        result = login_openrouter()

        assert result is not None
        assert result.provider == "openrouter"
        assert result.method == "api_key"
        assert result.token == "sk-or-key-123"

    @patch("cascade.auth_flow.webbrowser")
    @patch("cascade.auth_flow._prompt")
    def test_cancel(self, mock_prompt, mock_browser):
        mock_prompt.return_value = ""

        result = login_openrouter()

        assert result is None
