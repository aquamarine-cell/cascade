"""Tests for workflow definitions and runner."""

import pytest
from cascade.agents.schema import AgentDef
from cascade.agents.workflow import (
    WorkflowStep,
    WorkflowDef,
    WorkflowRunner,
    load_workflows_from_dict,
)


class TestWorkflowStep:
    def test_defaults(self):
        step = WorkflowStep(agent="planner")
        assert step.prompt_template == "{input}"
        assert step.label == ""

    def test_frozen(self):
        step = WorkflowStep(agent="x")
        with pytest.raises(AttributeError):
            step.agent = "y"


class TestWorkflowDef:
    def test_frozen(self):
        wf = WorkflowDef(name="test")
        with pytest.raises(AttributeError):
            wf.name = "other"

    def test_defaults(self):
        wf = WorkflowDef(name="test")
        assert wf.description == ""
        assert wf.steps == ()


class TestLoadWorkflowsFromDict:
    def test_basic_load(self):
        data = {
            "feature": {
                "description": "Plan then review",
                "steps": [
                    {"agent": "planner", "label": "Planning"},
                    {
                        "agent": "reviewer",
                        "prompt_template": "Review:\n{input}",
                        "label": "Review",
                    },
                ],
            },
        }
        wfs = load_workflows_from_dict(data)
        assert "feature" in wfs
        wf = wfs["feature"]
        assert wf.description == "Plan then review"
        assert len(wf.steps) == 2
        assert wf.steps[0].agent == "planner"
        assert wf.steps[1].prompt_template == "Review:\n{input}"

    def test_skips_invalid_entries(self):
        data = {
            "good": {
                "steps": [{"agent": "a"}],
            },
            "bad_no_steps": {"description": "missing steps"},
            "bad_not_dict": "nope",
        }
        wfs = load_workflows_from_dict(data)
        assert len(wfs) == 1
        assert "good" in wfs

    def test_skips_steps_without_agent(self):
        data = {
            "test": {
                "steps": [
                    {"agent": "ok", "label": "Good"},
                    {"label": "Missing agent"},
                ],
            },
        }
        wfs = load_workflows_from_dict(data)
        assert len(wfs["test"].steps) == 1

    def test_empty_steps_skipped(self):
        data = {"empty": {"steps": []}}
        wfs = load_workflows_from_dict(data)
        assert "empty" not in wfs

    def test_empty_dict(self):
        assert load_workflows_from_dict({}) == {}


class TestWorkflowRunner:
    def _make_runner(self, responses):
        """Create a mock runner that returns responses in order."""
        call_log = []
        idx = [0]

        class MockAgentRunner:
            def run(self, agent, prompt, extra_context=None):
                call_log.append({
                    "agent": agent.name,
                    "prompt": prompt,
                    "extra_context": extra_context,
                })
                result = responses[idx[0]]
                idx[0] += 1
                return result

        agents = {
            "planner": AgentDef(name="planner"),
            "reviewer": AgentDef(name="reviewer"),
        }
        return MockAgentRunner(), agents, call_log

    def test_single_step(self):
        runner, agents, log = self._make_runner(["planned result"])
        wf = WorkflowDef(
            name="simple",
            steps=(WorkflowStep(agent="planner"),),
        )
        printed = []
        wr = WorkflowRunner(runner, agents, print_fn=printed.append)
        result = wr.run(wf, "build auth")

        assert result == "planned result"
        assert len(log) == 1
        assert log[0]["prompt"] == "build auth"
        assert log[0]["extra_context"] is None

    def test_chained_steps(self):
        runner, agents, log = self._make_runner(["plan output", "review output"])
        wf = WorkflowDef(
            name="chain",
            steps=(
                WorkflowStep(agent="planner", label="Plan"),
                WorkflowStep(
                    agent="reviewer",
                    prompt_template="Review:\n{input}",
                    label="Review",
                ),
            ),
        )
        printed = []
        wr = WorkflowRunner(runner, agents, print_fn=printed.append)
        result = wr.run(wf, "build auth")

        assert result == "review output"
        assert len(log) == 2
        assert log[1]["prompt"] == "Review:\nplan output"
        assert log[1]["extra_context"] == "plan output"
        assert "[Plan]" in printed[0]
        assert "[Review]" in printed[1]

    def test_unknown_agent_raises(self):
        runner, agents, _ = self._make_runner([])
        wf = WorkflowDef(
            name="bad",
            steps=(WorkflowStep(agent="nonexistent"),),
        )
        wr = WorkflowRunner(runner, agents)
        with pytest.raises(RuntimeError, match="unknown agent"):
            wr.run(wf, "go")
