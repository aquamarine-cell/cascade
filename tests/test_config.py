"""Tests for configuration system."""

import pytest
import tempfile
from pathlib import Path
from cascade.config import ConfigManager


def test_config_creation():
    """Test config file creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))
        
        assert config_path.exists()
        assert "providers" in manager.data


def test_get_default_provider():
    """Test getting default provider."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))
        
        default = manager.get_default_provider()
        assert default == "gemini"


def test_env_var_resolution():
    """Test environment variable resolution."""
    import os
    os.environ["TEST_KEY"] = "test_value"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))
        
        resolved = manager._resolve_env_var("${TEST_KEY}")
        assert resolved == "test_value"


def test_non_env_var_passthrough():
    """Test that non-env-var values pass through."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))
        
        value = manager._resolve_env_var("plain_value")
        assert value == "plain_value"
