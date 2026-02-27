"""Cascade - Beautiful multi-model AI assistant CLI."""

__version__ = "0.1.0"
__author__ = "Eve"

from .cli import cli, get_app
from .providers import BaseProvider, GeminiProvider, ClaudeProvider
from .config import ConfigManager

__all__ = [
    "cli",
    "get_app",
    "BaseProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "ConfigManager",
]
