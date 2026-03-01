"""Tests for Shannon integration module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cascade.integrations.shannon import ShannonIntegration


@pytest.fixture
def shannon(tmp_path):
    """Create a ShannonIntegration with a fake shannon install."""
    shannon_dir = tmp_path / "shannon"
    shannon_dir.mkdir()
    script = shannon_dir / "shannon"
    script.write_text("#!/bin/bash\necho ok")
    script.chmod(0o755)

    integration = ShannonIntegration(config_path=str(shannon_dir))
    return integration


class TestFindPath:
    def test_config_path_found(self, shannon):
        """Config path takes priority."""
        result = shannon.find_path()
        assert result is not None
        assert (result / "shannon").is_file()

    def test_env_var_found(self, tmp_path):
        """$SHANNON_HOME is checked after config path."""
        shannon_dir = tmp_path / "shannon_env"
        shannon_dir.mkdir()
        (shannon_dir / "shannon").write_text("#!/bin/bash\necho ok")
        (shannon_dir / "shannon").chmod(0o755)

        with patch.dict(os.environ, {"SHANNON_HOME": str(shannon_dir)}):
            integration = ShannonIntegration(config_path="")
            result = integration.find_path()
            assert result == shannon_dir

    def test_no_path_found(self):
        """Returns None when no valid installation exists."""
        integration = ShannonIntegration(config_path="/nonexistent/path")
        with patch.dict(os.environ, {"SHANNON_HOME": ""}, clear=False):
            # Also patch _DEFAULT_PATHS to avoid hitting real filesystem
            with patch(
                "cascade.integrations.shannon._DEFAULT_PATHS",
                [Path("/nonexistent/a"), Path("/nonexistent/b")],
            ):
                result = integration.find_path()
                assert result is None


class TestEnsureRepo:
    def test_creates_symlink(self, shannon, tmp_path):
        """Creates symlink from cwd into repos dir."""
        shannon_path = shannon.find_path()
        with patch("cascade.integrations.shannon.Path.cwd", return_value=tmp_path):
            link = shannon.ensure_repo(shannon_path, "myrepo")
            assert link.is_symlink()
            assert link.resolve() == tmp_path.resolve()

    def test_skips_existing_correct_symlink(self, shannon, tmp_path):
        """Does not recreate symlink if it already points to cwd."""
        shannon_path = shannon.find_path()
        repos_dir = shannon_path / "repos"
        repos_dir.mkdir()
        link = repos_dir / "myrepo"
        link.symlink_to(tmp_path)

        with patch("cascade.integrations.shannon.Path.cwd", return_value=tmp_path):
            result = shannon.ensure_repo(shannon_path, "myrepo")
            assert result.resolve() == tmp_path.resolve()

    def test_replaces_stale_symlink(self, shannon, tmp_path):
        """Replaces symlink if it points to a different target."""
        shannon_path = shannon.find_path()
        repos_dir = shannon_path / "repos"
        repos_dir.mkdir()
        link = repos_dir / "myrepo"
        old_target = tmp_path / "old"
        old_target.mkdir()
        link.symlink_to(old_target)

        new_target = tmp_path / "new"
        new_target.mkdir()

        with patch("cascade.integrations.shannon.Path.cwd", return_value=new_target):
            result = shannon.ensure_repo(shannon_path, "myrepo")
            assert result.resolve() == new_target.resolve()


class TestBuildEnv:
    def test_forwards_anthropic_api_key(self, shannon):
        """ANTHROPIC_API_KEY is forwarded."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test123"}, clear=False):
            env = shannon.build_env()
            assert env["ANTHROPIC_API_KEY"] == "sk-ant-test123"

    def test_forwards_oauth_token(self, shannon):
        """CLAUDE_CODE_OAUTH_TOKEN is forwarded when no ANTHROPIC_API_KEY."""
        with patch.dict(
            os.environ,
            {"CLAUDE_CODE_OAUTH_TOKEN": "oauth-tok", "ANTHROPIC_API_KEY": ""},
            clear=False,
        ):
            env = shannon.build_env()
            assert env.get("CLAUDE_CODE_OAUTH_TOKEN") == "oauth-tok"

    def test_max_output_tokens_set(self, shannon):
        """CLAUDE_CODE_MAX_OUTPUT_TOKENS defaults to 64000."""
        with patch.dict(os.environ, {}, clear=False):
            env = shannon.build_env()
            assert env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"] == "64000"


class TestCmdStartStop:
    def test_reject_double_start(self, shannon):
        """Cannot start a second run while one is active."""
        shannon._process = MagicMock()
        shannon._process.poll.return_value = None  # still running

        result = shannon.cmd_start("https://example.com")
        assert result is False

    def test_stop_terminates_process(self, shannon):
        """Stop terminates the active process."""
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        shannon._process = mock_proc

        shannon.cmd_stop()

        mock_proc.terminate.assert_called_once()
        assert shannon._process is None

    def test_start_returns_false_when_not_found(self):
        """Returns False when Shannon is not installed."""
        integration = ShannonIntegration(config_path="/nonexistent")
        with patch(
            "cascade.integrations.shannon._DEFAULT_PATHS",
            [Path("/nonexistent/a")],
        ):
            with patch.dict(os.environ, {"SHANNON_HOME": ""}, clear=False):
                result = integration.cmd_start("https://example.com")
                assert result is False
