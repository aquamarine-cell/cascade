"""Base provider interface for all AI models."""

from abc import ABC, abstractmethod
from typing import Optional, Iterator
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    api_key: str
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


class BaseProvider(ABC):
    """Abstract base class for all AI providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Send a single prompt and get a complete response."""
        pass

    @abstractmethod
    def stream(
        self, 
        prompt: str, 
        system: Optional[str] = None
    ) -> Iterator[str]:
        """Stream tokens from the provider."""
        pass

    @abstractmethod
    def compare(self, prompt: str, system: Optional[str] = None) -> dict:
        """Generate and return structured comparison data."""
        pass

    def validate(self) -> bool:
        """Validate provider configuration and connectivity."""
        return bool(self.config.api_key and self.config.model)
