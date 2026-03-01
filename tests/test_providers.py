"""Tests for provider system."""

from cascade.providers.base import BaseProvider, ProviderConfig


def test_provider_config_creation():
    """Test creating provider configuration."""
    config = ProviderConfig(
        api_key="test_key",
        model="test-model",
        temperature=0.5,
        max_tokens=100,
    )
    
    assert config.api_key == "test_key"
    assert config.model == "test-model"
    assert config.temperature == 0.5
    assert config.max_tokens == 100


def test_provider_config_defaults():
    """Test provider config with defaults."""
    config = ProviderConfig(
        api_key="key",
        model="model",
    )
    
    assert config.temperature == 0.7
    assert config.max_tokens is None
    assert config.base_url is None


class MockProvider(BaseProvider):
    """Mock provider for testing."""
    
    def ask(self, prompt, system=None):
        return f"Mock response to: {prompt}"
    
    def stream(self, prompt, system=None):
        yield "Mock "
        yield "streaming "
        yield "response"
    
    def compare(self, prompt, system=None):
        return {
            "provider": self.name,
            "response": "Mock response",
            "length": 13,
        }


def test_mock_provider():
    """Test mock provider implementation."""
    config = ProviderConfig(api_key="key", model="mock")
    provider = MockProvider(config)
    
    assert provider.name == "MockProvider"
    assert provider.validate()
    
    # Test ask
    response = provider.ask("test")
    assert "Mock response" in response
    
    # Test stream
    streamed = "".join(provider.stream("test"))
    assert "Mock streaming response" in streamed
    
    # Test compare
    comparison = provider.compare("test")
    assert comparison["provider"] == "MockProvider"
    assert comparison["length"] == 13


def test_provider_validation():
    """Test provider validation."""
    # Valid config
    valid_config = ProviderConfig(api_key="key", model="model")
    provider = MockProvider(valid_config)
    assert provider.validate()
    
    # Invalid config (missing api_key)
    invalid_config = ProviderConfig(api_key="", model="model")
    provider = MockProvider(invalid_config)
    assert not provider.validate()
