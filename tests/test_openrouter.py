"""Tests for the OpenRouter provider."""

from cascade.providers.base import ProviderConfig
from cascade.providers.openrouter import OpenRouterProvider


def test_openrouter_accepts_provider_config():
    """OpenRouterProvider should accept a ProviderConfig (not a dict)."""
    config = ProviderConfig(
        api_key="test-key",
        model="qwen/qwen3.5-35b-a3b",
    )
    provider = OpenRouterProvider(config)
    assert provider.config is config
    assert provider.config.api_key == "test-key"
    assert provider.config.model == "qwen/qwen3.5-35b-a3b"


def test_openrouter_abc_compliance():
    """OpenRouterProvider should implement all BaseProvider abstract methods."""
    config = ProviderConfig(api_key="test-key", model="test-model")
    provider = OpenRouterProvider(config)
    assert hasattr(provider, "ask")
    assert hasattr(provider, "stream")
    assert hasattr(provider, "compare")
    assert callable(provider.ask)
    assert callable(provider.stream)
    assert callable(provider.compare)


def test_openrouter_default_base_url():
    """Should use OpenRouter base URL by default."""
    config = ProviderConfig(api_key="test-key", model="test-model")
    provider = OpenRouterProvider(config)
    assert provider.base_url == "https://openrouter.ai/api/v1"


def test_openrouter_custom_base_url():
    """Should accept a custom base URL."""
    config = ProviderConfig(
        api_key="test-key",
        model="test-model",
        base_url="https://custom.api/v1",
    )
    provider = OpenRouterProvider(config)
    assert provider.base_url == "https://custom.api/v1"


def test_openrouter_validation():
    """Should validate with valid config."""
    config = ProviderConfig(api_key="test-key", model="test-model")
    provider = OpenRouterProvider(config)
    assert provider.validate() is True


def test_openrouter_validation_no_key():
    """Should fail validation without API key."""
    config = ProviderConfig(api_key="", model="test-model")
    provider = OpenRouterProvider(config)
    assert provider.validate() is False
