"""Tests for the upgraded plugin system."""

from cascade.plugins.base import BasePlugin
from cascade.plugins.registry import get_plugin_registry, clear_plugin_registry, register_plugin
from cascade.plugins.file_ops import FileOpsPlugin


def test_file_ops_is_base_plugin():
    """FileOpsPlugin should be a BasePlugin subclass."""
    plugin = FileOpsPlugin()
    assert isinstance(plugin, BasePlugin)


def test_file_ops_name():
    plugin = FileOpsPlugin()
    assert plugin.name == "file_ops"


def test_file_ops_description():
    plugin = FileOpsPlugin()
    assert len(plugin.description) > 0


def test_file_ops_get_tools():
    plugin = FileOpsPlugin()
    tools = plugin.get_tools()
    assert "read_file" in tools
    assert "write_file" in tools
    assert "list_files" in tools
    assert "append_file" in tools
    assert callable(tools["read_file"])


def test_plugin_registry_has_file_ops():
    """file_ops should be auto-registered."""
    registry = get_plugin_registry()
    assert "file_ops" in registry


def test_register_custom_plugin():
    clear_plugin_registry()

    @register_plugin("custom")
    class CustomPlugin(BasePlugin):
        @property
        def name(self):
            return "custom"

        @property
        def description(self):
            return "test"

        def get_tools(self):
            return {"noop": lambda: None}

    registry = get_plugin_registry()
    assert "custom" in registry
    assert registry["custom"] is CustomPlugin


def test_plugin_configure_default():
    """Default configure() should be a no-op."""
    plugin = FileOpsPlugin()
    plugin.configure({"key": "value"})  # should not raise
