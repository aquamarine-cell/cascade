"""Decorator-based plugin registry (same pattern as provider registry)."""

from typing import Dict, Type

from .base import BasePlugin

_REGISTRY: Dict[str, Type[BasePlugin]] = {}


def register_plugin(name: str):
    """Decorator that registers a plugin class under the given name.

    Usage:
        @register_plugin("file_ops")
        class FileOpsPlugin(BasePlugin):
            ...
    """
    def decorator(cls: Type[BasePlugin]):
        if not issubclass(cls, BasePlugin):
            raise TypeError(f"{cls.__name__} must be a subclass of BasePlugin")
        _REGISTRY[name] = cls
        return cls
    return decorator


def get_plugin_registry() -> Dict[str, Type[BasePlugin]]:
    """Return a copy of the current plugin registry."""
    return dict(_REGISTRY)


def clear_plugin_registry() -> None:
    """Clear the registry. Primarily for testing."""
    _REGISTRY.clear()
