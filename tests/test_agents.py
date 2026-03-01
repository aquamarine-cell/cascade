"""Tests for the agent data layer -- schema + loader."""

import pytest
from cascade.agents.schema import AgentDef
from cascade.agents.loader import load_agents_from_dict


class TestAgentDef:
    def test_frozen(self):
        agent = AgentDef(name="test")
        with pytest.raises(AttributeError):
            agent.name = "other"

    def test_defaults(self):
        agent = AgentDef(name="a")
        assert agent.description == ""
        assert agent.provider is None
        assert agent.model is None
        assert agent.temperature is None
        assert agent.system_prompt == ""
        assert agent.allowed_tools is None
        assert agent.max_tokens is None

    def test_to_summary_minimal(self):
        agent = AgentDef(name="planner")
        assert "planner" in agent.to_summary()

    def test_to_summary_with_overrides(self):
        agent = AgentDef(
            name="builder",
            description="Builds things",
            provider="openai",
            model="gpt-5",
            allowed_tools=("read_file", "write_file"),
        )
        s = agent.to_summary()
        assert "builder" in s
        assert "Builds things" in s
        assert "provider=openai" in s
        assert "model=gpt-5" in s
        assert "tools=2" in s

    def test_allowed_tools_none_means_unrestricted(self):
        agent = AgentDef(name="x", allowed_tools=None)
        assert agent.allowed_tools is None

    def test_allowed_tools_empty_means_no_tools(self):
        agent = AgentDef(name="x", allowed_tools=())
        assert agent.allowed_tools == ()


class TestLoadAgentsFromDict:
    def test_basic_load(self):
        data = {
            "planner": {
                "description": "Plans features",
                "provider": "claude",
                "model": "claude-opus-4-6",
                "system_prompt": "You are a planner.",
            },
        }
        agents = load_agents_from_dict(data)
        assert "planner" in agents
        a = agents["planner"]
        assert a.name == "planner"
        assert a.description == "Plans features"
        assert a.provider == "claude"
        assert a.model == "claude-opus-4-6"
        assert a.system_prompt == "You are a planner."
        assert a.allowed_tools is None

    def test_allowed_tools_converted_to_tuple(self):
        data = {
            "reader": {
                "allowed_tools": ["read_file", "list_files"],
            },
        }
        agents = load_agents_from_dict(data)
        assert agents["reader"].allowed_tools == ("read_file", "list_files")

    def test_workflows_key_skipped(self):
        data = {
            "workflows": {"feature": {"steps": []}},
            "planner": {"description": "ok"},
        }
        agents = load_agents_from_dict(data)
        assert "workflows" not in agents
        assert "planner" in agents

    def test_invalid_entries_skipped(self):
        data = {
            "good": {"description": "works"},
            "bad_string": "not a dict",
            "bad_int": 42,
        }
        agents = load_agents_from_dict(data)
        assert len(agents) == 1
        assert "good" in agents

    def test_empty_dict(self):
        assert load_agents_from_dict({}) == {}

    def test_temperature_preserved(self):
        data = {"hot": {"temperature": 1.5}}
        agents = load_agents_from_dict(data)
        assert agents["hot"].temperature == 1.5

    def test_max_tokens_preserved(self):
        data = {"limited": {"max_tokens": 2048}}
        agents = load_agents_from_dict(data)
        assert agents["limited"].max_tokens == 2048
