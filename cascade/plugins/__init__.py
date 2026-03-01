"""Plugin system for extending Cascade."""

from .base import BasePlugin
from .file_ops import FileOpsPlugin
from .registry import register_plugin, get_plugin_registry

# Import reflection plugin to trigger registration
from ..tools.reflection import ReflectionPlugin

__all__ = [
    "BasePlugin",
    "FileOpsPlugin",
    "ReflectionPlugin",
    "register_plugin",
    "get_plugin_registry",
]
