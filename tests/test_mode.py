"""Tests for cascade.ui.mode."""

from cascade.ui.mode import ModeState, MODE_ORDER


def test_initial_state():
    state = ModeState()
    assert state.index == 0
    assert state.mode_name == "design"
    assert state.default_provider == "gemini"
    assert state.active_provider == "gemini"
    assert state.override_provider is None


def test_cycle_through_all_modes():
    state = ModeState()
    modes_seen = [state.mode_name]
    for _ in range(len(MODE_ORDER) - 1):
        state = state.cycle()
        modes_seen.append(state.mode_name)
    assert modes_seen == list(MODE_ORDER)


def test_cycle_wraps_around():
    state = ModeState()
    for _ in range(len(MODE_ORDER)):
        state = state.cycle()
    assert state.mode_name == "design"
    assert state.index == 0


def test_with_override():
    state = ModeState()
    overridden = state.with_override("claude")
    assert overridden.active_provider == "claude"
    assert overridden.default_provider == "gemini"
    assert overridden.override_provider == "claude"


def test_override_reset():
    state = ModeState().with_override("claude")
    reset = state.with_override(None)
    assert reset.active_provider == "gemini"
    assert reset.override_provider is None


def test_cycle_preserves_override():
    state = ModeState().with_override("claude")
    cycled = state.cycle()
    assert cycled.mode_name == "plan"
    assert cycled.active_provider == "claude"


def test_format_indicator():
    state = ModeState()
    indicator = state.format_indicator()
    assert "design" in indicator
    assert "gem" in indicator


def test_theme_property():
    state = ModeState(index=1)
    theme = state.theme
    assert theme.name == "claude"
    assert theme.abbreviation == "cla"


def test_mode_provider_mapping():
    expected = {
        "design": "gemini",
        "plan": "claude",
        "build": "openai",
        "test": "openrouter",
    }
    for i, mode in enumerate(MODE_ORDER):
        state = ModeState(index=i)
        assert state.mode_name == mode
        assert state.default_provider == expected[mode]


def test_immutability():
    state = ModeState()
    cycled = state.cycle()
    assert state.index == 0
    assert cycled.index == 1
    # Original unchanged
    assert state.mode_name == "design"
