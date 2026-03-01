"""Tests for ProviderResponse and last_usage plumbing."""

from cascade.providers.response import ProviderResponse
from cascade.providers.base import BaseProvider, ProviderConfig


class TestProviderResponse:
    def test_frozen_dataclass(self):
        r = ProviderResponse(text="hello", input_tokens=10, output_tokens=20)
        assert r.text == "hello"
        assert r.input_tokens == 10
        assert r.output_tokens == 20
        assert r.total_tokens == 30

    def test_defaults(self):
        r = ProviderResponse(text="hi")
        assert r.input_tokens == 0
        assert r.output_tokens == 0
        assert r.model == ""
        assert r.provider == ""
        assert r.latency_ms == 0.0

    def test_format_tokens_small(self):
        r = ProviderResponse(text="", input_tokens=50, output_tokens=100)
        assert "~50" in r.format_tokens()
        assert "~100" in r.format_tokens()

    def test_format_tokens_large(self):
        r = ProviderResponse(text="", input_tokens=1500, output_tokens=3200)
        assert "~1.5k" in r.format_tokens()
        assert "~3.2k" in r.format_tokens()

    def test_immutable(self):
        r = ProviderResponse(text="hello")
        try:
            r.text = "other"
            assert False, "should be frozen"
        except AttributeError:
            pass


class TestBaseProviderLastUsage:
    def test_last_usage_default_none(self):
        """BaseProvider starts with no usage data."""

        class DummyProvider(BaseProvider):
            def ask(self, prompt, system=None):
                return "ok"

            def stream(self, prompt, system=None):
                yield "ok"

            def compare(self, prompt, system=None):
                return {"provider": "dummy", "response": "ok"}

        config = ProviderConfig(api_key="test", model="test-model")
        prov = DummyProvider(config)
        assert prov.last_usage is None

    def test_last_usage_settable_by_subclass(self):
        class DummyProvider(BaseProvider):
            def ask(self, prompt, system=None):
                self._last_usage = (10, 20)
                return "ok"

            def stream(self, prompt, system=None):
                yield "ok"

            def compare(self, prompt, system=None):
                return {}

        config = ProviderConfig(api_key="test", model="test-model")
        prov = DummyProvider(config)
        prov.ask("test")
        assert prov.last_usage == (10, 20)
