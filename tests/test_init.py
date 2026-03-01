"""Tests for cascade.agents.templates and cascade.agents.init."""

import pytest
from pathlib import Path

from cascade.agents.templates import detect_project_type, get_template, PROJECT_TYPES
from cascade.agents.init import run_init


class TestDetectProjectType:
    """Tests for detect_project_type()."""

    def test_python_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").touch()
        assert detect_project_type(tmp_path) == "python"

    def test_python_setup_py(self, tmp_path):
        (tmp_path / "setup.py").touch()
        assert detect_project_type(tmp_path) == "python"

    def test_rust(self, tmp_path):
        (tmp_path / "Cargo.toml").touch()
        assert detect_project_type(tmp_path) == "rust"

    def test_go(self, tmp_path):
        (tmp_path / "go.mod").touch()
        assert detect_project_type(tmp_path) == "go"

    def test_web(self, tmp_path):
        (tmp_path / "package.json").touch()
        assert detect_project_type(tmp_path) == "web"

    def test_general_fallback(self, tmp_path):
        assert detect_project_type(tmp_path) == "general"

    def test_python_takes_priority_over_web(self, tmp_path):
        """If both pyproject.toml and package.json exist, python wins."""
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "package.json").touch()
        assert detect_project_type(tmp_path) == "python"


class TestGetTemplate:
    """Tests for get_template()."""

    def test_known_types_return_dicts(self):
        for pt in PROJECT_TYPES:
            tpl = get_template(pt)
            assert isinstance(tpl, dict)
            assert "system_prompt" in tpl
            assert "agents" in tpl
            assert "verify" in tpl

    def test_unknown_type_falls_back_to_general(self):
        tpl = get_template("unknown_type_xyz")
        general = get_template("general")
        assert tpl == general

    def test_project_types_sorted(self):
        assert PROJECT_TYPES == tuple(sorted(PROJECT_TYPES))

    def test_python_template_has_security_agent(self):
        tpl = get_template("python")
        assert "security" in tpl["agents"]

    def test_web_template_has_accessibility_agent(self):
        tpl = get_template("web")
        assert "accessibility" in tpl["agents"]


class TestRunInit:
    """Tests for run_init()."""

    def test_creates_cascade_dir(self, tmp_path):
        summary = run_init(tmp_path, "general")
        assert (tmp_path / ".cascade").is_dir()
        assert "general" in summary

    def test_creates_system_prompt(self, tmp_path):
        run_init(tmp_path, "python")
        sp = tmp_path / ".cascade" / "system_prompt.md"
        assert sp.is_file()
        content = sp.read_text()
        assert "Python" in content

    def test_creates_agents_yaml(self, tmp_path):
        run_init(tmp_path, "python")
        agents = tmp_path / ".cascade" / "agents.yaml"
        assert agents.is_file()
        import yaml
        data = yaml.safe_load(agents.read_text())
        assert "planner" in data
        assert "reviewer" in data

    def test_creates_context_dir(self, tmp_path):
        run_init(tmp_path, "general")
        assert (tmp_path / ".cascade" / "context").is_dir()

    def test_skips_existing_files(self, tmp_path):
        # First init
        run_init(tmp_path, "python")
        original_content = (tmp_path / ".cascade" / "system_prompt.md").read_text()

        # Second init -- should skip
        summary = run_init(tmp_path, "go")
        assert "already exists" in summary

        # Content should be unchanged (python template, not go)
        assert (tmp_path / ".cascade" / "system_prompt.md").read_text() == original_content

    def test_disable_system_prompt(self, tmp_path):
        run_init(tmp_path, "general", enable_system_prompt=False)
        assert not (tmp_path / ".cascade" / "system_prompt.md").exists()

    def test_disable_agents(self, tmp_path):
        run_init(tmp_path, "general", enable_agents=False)
        assert not (tmp_path / ".cascade" / "agents.yaml").exists()

    def test_disable_context(self, tmp_path):
        run_init(tmp_path, "general", enable_context=False)
        assert not (tmp_path / ".cascade" / "context").exists()

    def test_print_fn_receives_messages(self, tmp_path):
        messages = []
        run_init(tmp_path, "general", print_fn=messages.append)
        assert len(messages) > 0
        assert any("created" in m for m in messages)

    def test_summary_lists_created_files(self, tmp_path):
        summary = run_init(tmp_path, "general")
        assert "system_prompt.md" in summary
        assert "agents.yaml" in summary
        assert "context/" in summary
