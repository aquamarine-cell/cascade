"""Tests for the hook system: loading, running, and lifecycle events."""

import pytest

from cascade.hooks.runner import HookEvent, HookDefinition, HookRunner
from cascade.hooks.loader import load_hooks_from_config


class TestHookDefinition:
    """Tests for the frozen HookDefinition dataclass."""

    def test_frozen(self):
        hook = HookDefinition(
            name="test", event=HookEvent.BEFORE_ASK, command="echo hi",
        )
        with pytest.raises(AttributeError):
            hook.name = "changed"

    def test_defaults(self):
        hook = HookDefinition(
            name="test", event=HookEvent.BEFORE_ASK, command="echo hi",
        )
        assert hook.timeout == 30
        assert hook.enabled is True


class TestHookRunner:
    """Tests for HookRunner execution."""

    def test_empty_runner(self):
        runner = HookRunner()
        assert runner.hook_count == 0
        results = runner.run_hooks(HookEvent.BEFORE_ASK)
        assert results == []

    def test_run_echo_command(self):
        hook = HookDefinition(
            name="echo_test",
            event=HookEvent.BEFORE_ASK,
            command="echo hello",
        )
        runner = HookRunner(hooks=(hook,))
        results = runner.run_hooks(HookEvent.BEFORE_ASK)
        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["name"] == "echo_test"
        assert "hello" in results[0]["output"]

    def test_event_filtering(self):
        hook1 = HookDefinition(
            name="before", event=HookEvent.BEFORE_ASK, command="echo before",
        )
        hook2 = HookDefinition(
            name="after", event=HookEvent.AFTER_RESPONSE, command="echo after",
        )
        runner = HookRunner(hooks=(hook1, hook2))

        results = runner.run_hooks(HookEvent.BEFORE_ASK)
        assert len(results) == 1
        assert results[0]["name"] == "before"

    def test_disabled_hooks_skipped(self):
        hook = HookDefinition(
            name="disabled",
            event=HookEvent.BEFORE_ASK,
            command="echo should not run",
            enabled=False,
        )
        runner = HookRunner(hooks=(hook,))
        results = runner.run_hooks(HookEvent.BEFORE_ASK)
        assert results == []

    def test_context_as_env_vars(self):
        hook = HookDefinition(
            name="env_test",
            event=HookEvent.BEFORE_ASK,
            command='echo $CASCADE_EVENT $CASCADE_PROVIDER',
        )
        runner = HookRunner(hooks=(hook,))
        results = runner.run_hooks(
            HookEvent.BEFORE_ASK,
            context={"provider": "claude"},
        )
        assert results[0]["success"] is True
        output = results[0]["output"]
        assert "before_ask" in output
        assert "claude" in output

    def test_failing_command(self):
        hook = HookDefinition(
            name="fail",
            event=HookEvent.ON_ERROR,
            command="exit 1",
        )
        runner = HookRunner(hooks=(hook,))
        results = runner.run_hooks(HookEvent.ON_ERROR)
        assert len(results) == 1
        assert results[0]["success"] is False
        assert results[0]["return_code"] == 1

    def test_timeout(self):
        hook = HookDefinition(
            name="slow",
            event=HookEvent.ON_EXIT,
            command="sleep 10",
            timeout=1,
        )
        runner = HookRunner(hooks=(hook,))
        results = runner.run_hooks(HookEvent.ON_EXIT)
        assert results[0]["success"] is False
        assert "timed out" in results[0]["output"].lower()

    def test_multiple_hooks_same_event(self):
        hooks = tuple(
            HookDefinition(
                name=f"hook_{i}",
                event=HookEvent.AFTER_RESPONSE,
                command=f"echo {i}",
            )
            for i in range(3)
        )
        runner = HookRunner(hooks=hooks)
        results = runner.run_hooks(HookEvent.AFTER_RESPONSE)
        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_describe(self):
        hook = HookDefinition(
            name="test", event=HookEvent.BEFORE_ASK, command="echo test",
        )
        runner = HookRunner(hooks=(hook,))
        desc = runner.describe()
        assert len(desc) == 1
        assert desc[0]["name"] == "test"
        assert desc[0]["event"] == "before_ask"
        assert desc[0]["command"] == "echo test"
        assert desc[0]["enabled"] is True

    def test_hooks_for_event(self):
        h1 = HookDefinition(name="a", event=HookEvent.BEFORE_ASK, command="echo a")
        h2 = HookDefinition(name="b", event=HookEvent.ON_EXIT, command="echo b")
        h3 = HookDefinition(name="c", event=HookEvent.BEFORE_ASK, command="echo c")
        runner = HookRunner(hooks=(h1, h2, h3))

        before_hooks = runner.hooks_for_event(HookEvent.BEFORE_ASK)
        assert len(before_hooks) == 2


class TestLoadHooksFromConfig:
    """Tests for parsing hook definitions from config YAML data."""

    def test_valid_hooks(self):
        data = [
            {
                "name": "pre_check",
                "event": "before_ask",
                "command": "echo checking",
                "timeout": 10,
            },
            {
                "name": "post_log",
                "event": "after_response",
                "command": "echo done",
                "enabled": False,
            },
        ]
        hooks = load_hooks_from_config(data)
        assert len(hooks) == 2
        assert hooks[0].name == "pre_check"
        assert hooks[0].event == HookEvent.BEFORE_ASK
        assert hooks[0].timeout == 10
        assert hooks[1].enabled is False

    def test_invalid_event_skipped(self):
        data = [
            {"name": "bad", "event": "nonexistent_event", "command": "echo"},
        ]
        hooks = load_hooks_from_config(data)
        assert len(hooks) == 0

    def test_missing_fields_skipped(self):
        data = [
            {"name": "no_command", "event": "before_ask"},
            {"event": "before_ask", "command": "echo"},
            {"name": "no_event", "command": "echo"},
        ]
        hooks = load_hooks_from_config(data)
        assert len(hooks) == 0

    def test_non_dict_entries_skipped(self):
        data = ["not a dict", 42, None]
        hooks = load_hooks_from_config(data)
        assert len(hooks) == 0

    def test_empty_list(self):
        hooks = load_hooks_from_config([])
        assert hooks == ()

    def test_all_events(self):
        data = [
            {"name": f"hook_{e}", "event": e, "command": f"echo {e}"}
            for e in ("before_ask", "after_response", "on_exit", "on_error")
        ]
        hooks = load_hooks_from_config(data)
        assert len(hooks) == 4
        events = {h.event for h in hooks}
        assert events == {
            HookEvent.BEFORE_ASK,
            HookEvent.AFTER_RESPONSE,
            HookEvent.ON_EXIT,
            HookEvent.ON_ERROR,
        }
