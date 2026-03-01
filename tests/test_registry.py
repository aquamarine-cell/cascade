"""Tests for the provider registry system."""

from cascade.providers.base import BaseProvider
from cascade.providers.registry import (
    register_provider,
    discover_providers,
    get_registry,
    clear_registry,
)


def test_discover_finds_all_providers():
    """discover_providers should find all decorated provider modules."""
    clear_registry()
    discover_providers()
    registry = get_registry()
    assert "gemini" in registry
    assert "claude" in registry
    assert "openrouter" in registry
    assert "openai" in registry


def test_registry_returns_base_provider_subclasses():
    """All registered classes must be BaseProvider subclasses."""
    clear_registry()
    discover_providers()
    for name, cls in get_registry().items():
        assert issubclass(cls, BaseProvider), f"{name} is not a BaseProvider subclass"


def test_register_custom_provider():
    """@register_provider should register a custom class."""
    clear_registry()

    @register_provider("custom")
    class CustomProvider(BaseProvider):
        def ask(self, prompt, system=None):
            return "ok"

        def stream(self, prompt, system=None):
            yield "ok"

        def compare(self, prompt, system=None):
            return {"response": "ok"}

    registry = get_registry()
    assert "custom" in registry
    assert registry["custom"] is CustomProvider


def test_clear_registry():
    """clear_registry should empty the registry."""
    clear_registry()
    discover_providers()
    assert len(get_registry()) > 0
    clear_registry()
    assert len(get_registry()) == 0


def test_get_registry_returns_copy():
    """get_registry should return a copy, not the internal dict."""
    clear_registry()
    discover_providers()
    reg1 = get_registry()
    reg1["fake"] = None
    reg2 = get_registry()
    assert "fake" not in reg2
