"""Tests for the OpenAI provider."""

from cascade.providers.base import ProviderConfig
from cascade.providers.openai_provider import OpenAIProvider


def test_openai_accepts_provider_config():
    """OpenAIProvider should accept a ProviderConfig."""
    config = ProviderConfig(
        api_key="test-key",
        model="gpt-4o",
    )
    provider = OpenAIProvider(config)
    assert provider.config is config
    assert provider.config.api_key == "test-key"
    assert provider.config.model == "gpt-4o"


def test_openai_abc_compliance():
    """OpenAIProvider should implement all BaseProvider abstract methods."""
    config = ProviderConfig(api_key="test-key", model="test-model")
    provider = OpenAIProvider(config)
    assert hasattr(provider, "ask")
    assert hasattr(provider, "stream")
    assert hasattr(provider, "compare")
    assert callable(provider.ask)
    assert callable(provider.stream)
    assert callable(provider.compare)


def test_openai_default_base_url():
    """Should use OpenAI base URL by default."""
    config = ProviderConfig(api_key="test-key", model="gpt-4o")
    provider = OpenAIProvider(config)
    assert provider.base_url == "https://api.openai.com/v1"


def test_openai_custom_base_url():
    """Should accept custom base URL for Azure/proxies."""
    config = ProviderConfig(
        api_key="test-key",
        model="gpt-4",
        base_url="https://my-azure.openai.azure.com/v1",
    )
    provider = OpenAIProvider(config)
    assert provider.base_url == "https://my-azure.openai.azure.com/v1"


def test_openai_validation():
    """Should validate with valid config."""
    config = ProviderConfig(api_key="sk-test", model="gpt-4o")
    provider = OpenAIProvider(config)
    assert provider.validate() is True


def test_openai_validation_no_key():
    """Should fail validation without API key."""
    config = ProviderConfig(api_key="", model="gpt-4o")
    provider = OpenAIProvider(config)
    assert provider.validate() is False
