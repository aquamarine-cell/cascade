"""Tests for /upload and /context command handlers."""

from unittest.mock import MagicMock, patch

from cascade.context.memory import ContextBuilder
from cascade.commands import CommandHandler, COMMANDS


class TestUploadCommandDef:
    """Verify the command definitions exist."""

    def test_upload_command_registered(self):
        names = [c.name for c in COMMANDS]
        assert "upload" in names

    def test_context_command_registered(self):
        names = [c.name for c in COMMANDS]
        assert "context" in names

    def test_init_command_registered(self):
        names = [c.name for c in COMMANDS]
        assert "init" in names


class TestContextCommand:
    """Tests for _cmd_context()."""

    def _make_handler(self):
        app = MagicMock()
        cli_app = MagicMock()
        cli_app.context_builder = ContextBuilder()
        app.cli_app = cli_app
        handler = CommandHandler(app)
        # Capture posted messages
        posted = []
        handler._post_system = lambda msg: posted.append(msg)
        return handler, cli_app.context_builder, posted

    def test_context_empty(self):
        handler, ctx, posted = self._make_handler()
        handler._cmd_context([])
        assert len(posted) == 1
        assert "No uploaded context" in posted[0]

    def test_context_with_sources(self):
        handler, ctx, posted = self._make_handler()
        ctx.add_text("hello world", label="test.txt")
        handler._cmd_context([])
        assert len(posted) == 1
        assert "test.txt" in posted[0]
        assert "1" in posted[0]  # source count

    def test_context_clear(self):
        handler, ctx, posted = self._make_handler()
        ctx.add_text("hello world", label="test.txt")
        assert ctx.source_count == 1
        handler._cmd_context(["clear"])
        assert ctx.source_count == 0
        assert "cleared" in posted[0].lower()


class TestUploadCommand:
    """Tests for _cmd_upload()."""

    def _make_handler(self):
        app = MagicMock()
        cli_app = MagicMock()
        cli_app.context_builder = ContextBuilder()
        app.cli_app = cli_app
        handler = CommandHandler(app)
        posted = []
        handler._post_system = lambda msg: posted.append(msg)
        return handler, cli_app.context_builder, posted

    def test_upload_status_not_running(self):
        handler, ctx, posted = self._make_handler()
        handler._cmd_upload(["status"])
        assert "stopped" in posted[0].lower()

    def test_upload_stop_not_running(self):
        handler, ctx, posted = self._make_handler()
        handler._cmd_upload(["stop"])
        assert "not running" in posted[0].lower()

    def test_upload_stop_running(self):
        handler, ctx, posted = self._make_handler()
        mock_server = MagicMock()
        mock_server.running = True
        handler._upload_server = mock_server
        handler._cmd_upload(["stop"])
        mock_server.stop.assert_called_once()
        assert "stopped" in posted[0].lower()

    def test_upload_already_running(self):
        handler, ctx, posted = self._make_handler()
        mock_server = MagicMock()
        mock_server.running = True
        mock_server.host = "0.0.0.0"
        mock_server.port = 9222
        handler._upload_server = mock_server
        handler._cmd_upload([])
        assert "already running" in posted[0].lower()

    @patch("cascade.commands.CommandHandler._post_system")
    def test_upload_missing_deps(self, mock_post):
        handler, ctx, posted = self._make_handler()
        with patch.dict("sys.modules", {"cascade.web.server": None}):
            # Force ImportError by patching the import
            original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

            def fake_import(name, *args, **kwargs):
                if name == "cascade.web.server" or (
                    "web" in name and "server" in name
                ):
                    raise ImportError("no web")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=fake_import):
                handler._cmd_upload([])
                # Should report missing deps
                assert any("not installed" in p.lower() for p in posted)

    def test_upload_status_with_sources(self):
        handler, ctx, posted = self._make_handler()
        ctx.add_text("some content", label="doc.txt")
        handler._cmd_upload(["status"])
        assert "1" in posted[0]  # source count


class TestInitCommand:
    """Tests for _cmd_init()."""

    def _make_handler(self):
        app = MagicMock()
        cli_app = MagicMock()
        app.cli_app = cli_app
        handler = CommandHandler(app)
        posted = []
        handler._post_system = lambda msg: posted.append(msg)
        return handler, posted

    def test_init_warns_if_exists(self, tmp_path, monkeypatch):
        handler, posted = self._make_handler()
        # Create existing .cascade with agents.yaml
        cascade_dir = tmp_path / ".cascade"
        cascade_dir.mkdir()
        (cascade_dir / "agents.yaml").touch()

        monkeypatch.chdir(tmp_path)
        handler._cmd_init([])
        assert any("already exists" in p for p in posted)

    def test_init_runs_worker_for_new_project(self, tmp_path, monkeypatch):
        handler, posted = self._make_handler()
        monkeypatch.chdir(tmp_path)

        # _run_in_worker is called for new projects; mock it to capture the fn
        captured = []
        handler._run_in_worker = lambda fn, label="": captured.append(fn)

        handler._cmd_init(["general"])
        assert len(captured) == 1

        # Execute the captured function to verify it works
        result = captured[0]()
        assert "general" in result
        assert (tmp_path / ".cascade").is_dir()


class TestConfigReloadCommand:
    """Tests for /config reload behavior."""

    class _DummyConfig:
        def __init__(self):
            self.data = {}

    def _make_handler(self):
        app = MagicMock()
        app.state.provider_tokens = {}
        app.screen = MagicMock()

        cli_app = MagicMock()
        cli_app.providers = {"old": MagicMock()}
        cli_app.config = self._DummyConfig()
        cli_app._apply_detected_credentials = MagicMock()
        cli_app._build_prompt_pipeline = MagicMock(return_value="pipeline")

        def _init():
            cli_app.providers = {"new": MagicMock()}

        cli_app._init_providers = MagicMock(side_effect=_init)

        app.cli_app = cli_app
        handler = CommandHandler(app)
        posted = []
        handler._post_system = lambda msg: posted.append(msg)
        return handler, cli_app, posted

    @patch("cascade.auth.detect_all")
    def test_config_reload_refreshes_credentials_and_provider_set(self, mock_detect):
        mock_detect.return_value = ["cred"]
        handler, cli_app, posted = self._make_handler()

        handler._cmd_config(["reload"])

        assert cli_app.credentials == ["cred"]
        cli_app._apply_detected_credentials.assert_called_once()
        cli_app._init_providers.assert_called_once()
        assert set(cli_app.providers.keys()) == {"new"}
        assert posted
        assert "Config reloaded." in posted[-1]
        assert "Added: new" in posted[-1]
        assert "Removed: old" in posted[-1]
