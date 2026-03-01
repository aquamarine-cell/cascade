"""Tests for project context loading."""

import os

from cascade.context.project import ProjectContext


def test_no_cascade_dir(tmp_path):
    """No .cascade/ -> found is False."""
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert ctx.found is False
    assert ctx.system_prompt == ""
    assert ctx.agents == {}
    assert ctx.context_files == {}


def test_empty_cascade_dir(tmp_path):
    """Empty .cascade/ dir -> found is True, everything empty."""
    (tmp_path / ".cascade").mkdir()
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert ctx.found is True
    assert ctx.system_prompt == ""


def test_system_prompt(tmp_path):
    """system_prompt.md should be loaded."""
    cascade_dir = tmp_path / ".cascade"
    cascade_dir.mkdir()
    (cascade_dir / "system_prompt.md").write_text("You are a helpful assistant.")
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert ctx.system_prompt == "You are a helpful assistant."


def test_agents_yaml(tmp_path):
    """agents.yaml should be parsed into a dict."""
    cascade_dir = tmp_path / ".cascade"
    cascade_dir.mkdir()
    (cascade_dir / "agents.yaml").write_text(
        "coder:\n  provider: claude\n  model: claude-3-5-sonnet\n"
    )
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert "coder" in ctx.agents
    assert ctx.agents["coder"]["provider"] == "claude"


def test_context_files(tmp_path):
    """Files in .cascade/context/ should be loaded."""
    cascade_dir = tmp_path / ".cascade"
    context_dir = cascade_dir / "context"
    context_dir.mkdir(parents=True)
    (context_dir / "architecture.md").write_text("# Architecture\nMicroservices")
    (context_dir / "design.md").write_text("# Design\nClean code")
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert "architecture.md" in ctx.context_files
    assert "design.md" in ctx.context_files
    assert "Microservices" in ctx.context_files["architecture.md"]


def test_walk_up_to_find_cascade(tmp_path):
    """Should walk up parent directories to find .cascade/."""
    (tmp_path / ".cascade").mkdir()
    (tmp_path / ".cascade" / "system_prompt.md").write_text("root prompt")
    subdir = tmp_path / "src" / "components"
    subdir.mkdir(parents=True)
    ctx = ProjectContext(start_dir=str(subdir))
    assert ctx.found is True
    assert ctx.system_prompt == "root prompt"


def test_full_system_prompt(tmp_path):
    """get_full_system_prompt includes both prompt and context files."""
    cascade_dir = tmp_path / ".cascade"
    context_dir = cascade_dir / "context"
    context_dir.mkdir(parents=True)
    (cascade_dir / "system_prompt.md").write_text("Be concise.")
    (context_dir / "notes.md").write_text("Important note")
    ctx = ProjectContext(start_dir=str(tmp_path))
    full = ctx.get_full_system_prompt()
    assert "Be concise." in full
    assert "Important note" in full
    assert "Reference Materials" in full


def test_summary(tmp_path):
    cascade_dir = tmp_path / ".cascade"
    context_dir = cascade_dir / "context"
    context_dir.mkdir(parents=True)
    (cascade_dir / "system_prompt.md").write_text("prompt")
    (context_dir / "file.md").write_text("data")
    ctx = ProjectContext(start_dir=str(tmp_path))
    s = ctx.summary()
    assert "system prompt" in s
    assert "1 context file" in s


def test_summary_no_context(tmp_path):
    ctx = ProjectContext(start_dir=str(tmp_path))
    assert ctx.summary() == "No project context"
