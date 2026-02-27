"""Configuration management for Cascade."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from .providers.base import ProviderConfig


class ConfigManager:
    """Manage Cascade configuration from YAML."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or "~/.config/cascade/config.yaml").expanduser()
        self.data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            self._create_default_config()
            return self._read_yaml()
        
        return self._read_yaml()

    def _read_yaml(self) -> Dict[str, Any]:
        """Read and parse YAML file."""
        try:
            with open(self.config_path, "r") as f:
                content = yaml.safe_load(f)
                return content or {}
        except Exception as e:
            print(f"Error reading config: {e}")
            return {}

    def _create_default_config(self) -> None:
        """Create default configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            "providers": {
                "gemini": {
                    "enabled": False,
                    "api_key": "${GEMINI_API_KEY}",
                    "model": "gemini-2.0-flash",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                "claude": {
                    "enabled": False,
                    "api_key": "${CLAUDE_API_KEY}",
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            },
            "defaults": {
                "provider": "gemini",
                "theme": "deep-stream",
            },
        }
        
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        provider_data = self.data.get("providers", {}).get(provider_name, {})
        
        if not provider_data.get("enabled", False):
            return None
        
        api_key = self._resolve_env_var(provider_data.get("api_key", ""))
        if not api_key:
            return None
        
        return ProviderConfig(
            api_key=api_key,
            model=provider_data.get("model", ""),
            base_url=provider_data.get("base_url"),
            temperature=provider_data.get("temperature", 0.7),
            max_tokens=provider_data.get("max_tokens"),
        )

    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variable references like ${VAR_NAME}."""
        if not value.startswith("${") or not value.endswith("}"):
            return value
        
        var_name = value[2:-1]
        return os.getenv(var_name, "")

    def get_default_provider(self) -> str:
        """Get the default provider name."""
        return self.data.get("defaults", {}).get("provider", "gemini")

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names."""
        providers = self.data.get("providers", {})
        return [name for name, config in providers.items() if config.get("enabled", False)]

    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            yaml.dump(self.data, f, default_flow_style=False)
