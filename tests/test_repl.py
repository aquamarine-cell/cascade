"""Tests for the REPL modules."""

from unittest.mock import MagicMock

from cascade.repl import CascadeREPL


def _make_mock_app():
    app = MagicMock()
    app.config.get_default_provider.return_value = "gemini"
    app.providers = {"gemini": MagicMock()}
    app.providers["gemini"].config.model = "gemini-2.0-flash"
    return app


def test_repl_handle_exit():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    assert repl.handle_command("/exit") is False


def test_repl_handle_quit():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    assert repl.handle_command("/quit") is False


def test_repl_handle_providers():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    assert repl.handle_command("/providers") is True


def test_repl_handle_unknown_command():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    assert repl.handle_command("/foobar") is True


def test_repl_handle_regular_text():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    assert repl.handle_command("hello world") is True


def test_repl_switch_provider():
    app = _make_mock_app()
    app.providers["claude"] = MagicMock()
    repl = CascadeREPL(app)
    repl.switch_provider("claude")
    assert repl.current_provider == "claude"


def test_repl_switch_nonexistent():
    app = _make_mock_app()
    repl = CascadeREPL(app)
    repl.switch_provider("nonexistent")
    assert repl.current_provider == "gemini"


def test_prompt_repl_importable():
    """CascadePromptREPL should be importable when prompt_toolkit is installed."""
    from cascade.repl_prompt import CascadePromptREPL
    assert CascadePromptREPL is not None
