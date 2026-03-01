"""Tests for CLI credential detection (cascade.auth)."""

import json
from unittest.mock import patch


from cascade.auth import (
    DetectedCredential,
    _decode_jwt_payload,
    _read_json,
    detect_all,
    detect_claude,
    detect_codex,
    detect_gemini,
    format_auth_summary,
)


class TestReadJson:
    def test_reads_valid_json(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text('{"key": "value"}')
        assert _read_json(p) == {"key": "value"}

    def test_returns_none_for_missing(self, tmp_path):
        assert _read_json(tmp_path / "nope.json") is None

    def test_returns_none_for_bad_json(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("not json")
        assert _read_json(p) is None


class TestDecodeJwtPayload:
    def test_decodes_simple_jwt(self):
        import base64

        payload = base64.urlsafe_b64encode(
            json.dumps({"email": "test@example.com"}).encode()
        ).rstrip(b"=").decode()
        token = f"header.{payload}.signature"
        result = _decode_jwt_payload(token)
        assert result["email"] == "test@example.com"

    def test_returns_empty_for_invalid(self):
        assert _decode_jwt_payload("not-a-jwt") == {}

    def test_returns_empty_for_empty(self):
        assert _decode_jwt_payload("") == {}


class TestDetectClaude:
    def test_detects_claude_creds(self, tmp_path):
        creds_dir = tmp_path / ".claude"
        creds_dir.mkdir()
        creds_file = creds_dir / ".credentials.json"
        creds_file.write_text(json.dumps({
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-test-token",
                "subscriptionType": "max",
            }
        }))

        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            result = detect_claude()

        assert result is not None
        assert result.provider == "claude"
        assert result.token == "sk-ant-oat01-test-token"
        assert result.plan == "max"
        assert result.source == "Claude Code CLI"

    def test_returns_none_when_missing(self, tmp_path):
        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            assert detect_claude() is None

    def test_returns_none_when_no_token(self, tmp_path):
        creds_dir = tmp_path / ".claude"
        creds_dir.mkdir()
        (creds_dir / ".credentials.json").write_text(
            json.dumps({"claudeAiOauth": {}})
        )
        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            assert detect_claude() is None


class TestDetectGemini:
    def test_detects_gemini_creds(self, tmp_path):
        import base64

        email_payload = base64.urlsafe_b64encode(
            json.dumps({"email": "user@gmail.com"}).encode()
        ).rstrip(b"=").decode()
        id_token = f"header.{email_payload}.sig"

        gemini_dir = tmp_path / ".gemini"
        gemini_dir.mkdir()
        (gemini_dir / "oauth_creds.json").write_text(json.dumps({
            "access_token": "ya29.test-token",
            "id_token": id_token,
        }))

        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            result = detect_gemini()

        assert result is not None
        assert result.provider == "gemini"
        assert result.token == "ya29.test-token"
        assert result.email == "user@gmail.com"
        assert result.plan == "Google One AI Pro"

    def test_returns_none_when_missing(self, tmp_path):
        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            assert detect_gemini() is None


class TestDetectCodex:
    def test_detects_codex_creds(self, tmp_path):
        import base64

        payload_data = {
            "email": "user@example.com",
            "https://api.openai.com/auth": {
                "chatgpt_plan_type": "plus",
            },
        }
        id_payload = base64.urlsafe_b64encode(
            json.dumps(payload_data).encode()
        ).rstrip(b"=").decode()
        id_token = f"header.{id_payload}.sig"

        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()
        (codex_dir / "auth.json").write_text(json.dumps({
            "tokens": {
                "access_token": "eyJ-access-token",
                "id_token": id_token,
            }
        }))

        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            result = detect_codex()

        assert result is not None
        assert result.provider == "openai"
        assert result.token == "eyJ-access-token"
        assert result.email == "user@example.com"
        assert result.plan == "plus"

    def test_returns_none_when_missing(self, tmp_path):
        with patch("cascade.auth.Path") as mock_path:
            mock_path.home.return_value = tmp_path
            assert detect_codex() is None


class TestDetectAll:
    def test_collects_all_found(self):
        cred = DetectedCredential("test", "Test CLI", "tok", "e@x.com", "free")
        with patch("cascade.auth.detect_claude", return_value=cred), \
             patch("cascade.auth.detect_gemini", return_value=None), \
             patch("cascade.auth.detect_codex", return_value=cred):
            results = detect_all()
        assert len(results) == 2

    def test_empty_when_nothing_found(self):
        with patch("cascade.auth.detect_claude", return_value=None), \
             patch("cascade.auth.detect_gemini", return_value=None), \
             patch("cascade.auth.detect_codex", return_value=None):
            assert detect_all() == []


class TestFormatAuthSummary:
    def test_formats_single(self):
        creds = [
            DetectedCredential("gemini", "Gemini CLI", "tok", "a@b.com", "Pro"),
        ]
        result = format_auth_summary(creds)
        assert "Gemini CLI" in result
        assert "a@b.com" in result
        assert "Pro" in result

    def test_formats_multiple(self):
        creds = [
            DetectedCredential("claude", "Claude Code CLI", "t", "", "max"),
            DetectedCredential("gemini", "Gemini CLI", "t", "a@b.com", ""),
        ]
        result = format_auth_summary(creds)
        assert "Claude Code CLI" in result
        assert "Gemini CLI" in result

    def test_empty_when_none(self):
        assert format_auth_summary([]) == ""
