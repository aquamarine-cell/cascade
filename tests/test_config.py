"""Tests for configuration system."""

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


def test_apply_credential_enables_provider():
    """Test that apply_credential enables a provider with a token."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))

        # gemini starts disabled in default config
        assert manager.get_provider_config("gemini") is None

        manager.apply_credential("gemini", "ya29.test-token")
        config = manager.get_provider_config("gemini")
        assert config is not None
        assert config.api_key == "ya29.test-token"
        # Model comes from the default config (already set before apply_credential)
        assert config.model == "gemini-3.1-pro-preview"


def test_apply_credential_does_not_overwrite_existing():
    """Test that apply_credential skips already-configured providers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))

        # Manually enable with a key
        manager.data["providers"]["gemini"]["enabled"] = True
        manager.data["providers"]["gemini"]["api_key"] = "my-real-key"

        manager.apply_credential("gemini", "ya29.should-be-ignored")
        config = manager.get_provider_config("gemini")
        assert config.api_key == "my-real-key"


def test_apply_credential_new_provider():
    """Test that apply_credential works for a provider not in default config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(str(config_path))

        manager.apply_credential("openai", "sk-test-token")
        config = manager.get_provider_config("openai")
        assert config is not None
        assert config.api_key == "sk-test-token"
