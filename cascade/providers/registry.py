"""Self-registering provider registry.

Providers register themselves via the @register_provider decorator.
Call discover_providers() once at startup to import all provider modules,
which triggers the decorators and populates the registry.
"""

import importlib
import pkgutil
import sys
from typing import Dict, Type

from .base import BaseProvider

_REGISTRY: Dict[str, Type[BaseProvider]] = {}


def register_provider(name: str):
    """Decorator that registers a provider class under the given name.

    Usage:
        @register_provider("gemini")
        class GeminiProvider(BaseProvider):
            ...
    """
    def decorator(cls: Type[BaseProvider]):
        if not issubclass(cls, BaseProvider):
            raise TypeError(f"{cls.__name__} must be a subclass of BaseProvider")
        _REGISTRY[name] = cls
        return cls
    return decorator


def discover_providers() -> None:
    """Import all modules in the providers package to trigger @register_provider decorators.

    If a module is already imported (cached in sys.modules), it is reloaded
    so that the @register_provider decorators re-execute. This keeps the
    registry consistent even after clear_registry().
    """
    package = importlib.import_module("cascade.providers")
    for _importer, module_name, _is_pkg in pkgutil.iter_modules(package.__path__):
        if module_name in ("base", "registry", "__init__"):
            continue
        fqn = f"cascade.providers.{module_name}"
        if fqn in sys.modules:
            importlib.reload(sys.modules[fqn])
        else:
            importlib.import_module(fqn)


def get_registry() -> Dict[str, Type[BaseProvider]]:
    """Return the current provider registry (name -> class)."""
    return dict(_REGISTRY)


def clear_registry() -> None:
    """Clear the registry. Primarily for testing."""
    _REGISTRY.clear()
