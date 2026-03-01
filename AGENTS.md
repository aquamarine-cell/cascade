# Repository Guidelines

## Project Structure & Module Organization
- `cascade/` contains the application code.
- `cascade/providers/` holds model adapters; `cascade/tools/`, `cascade/plugins/`, and `cascade/hooks/` hold extensibility points.
- `cascade/ui/`, `cascade/widgets/`, and `cascade/screens/` implement terminal/TUI presentation.
- `cascade/agents/`, `cascade/prompts/`, and `cascade/context/` manage orchestration, prompts, and project memory.
- `cascade/web/` contains optional web upload/server integration.
- `tests/` contains pytest suites named `test_*.py`; add tests near the feature area you change.
- Top-level docs live in `README.md`, `DEVELOPMENT.md`, and `design.md`.

## Build, Test, and Development Commands
- `python -m venv venv && source venv/bin/activate`: create and activate a local virtualenv.
- `pip install -e ".[dev]"`: install Cascade in editable mode with test/lint tooling.
- `cascade --help`: check the REPL entrypoint and available runtime options.
- `cascade-cli --help`: check CLI command mode.
- `pytest`: run the full test suite (configured in `pyproject.toml`).
- `pytest --cov=cascade --cov-report=term-missing`: run coverage for changed areas.
- `ruff check cascade tests`: lint code.
- `ruff format cascade tests`: apply formatting.

## Coding Style & Naming Conventions
- Target Python 3.9+ and use 4-space indentation.
- Keep lines at or below 100 chars (Ruff config).
- Follow naming norms: `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Prefer type hints on public APIs and concise docstrings for non-obvious behavior.

## Testing Guidelines
- Framework: `pytest` with test discovery rooted at `tests/`.
- Test files should be named `test_<feature>.py`; test functions should describe behavior, e.g., `test_apply_credential_new_provider`.
- Add or update tests for every behavior change, especially around providers, tools, auth, and REPL flows.

## Commit & Pull Request Guidelines
- Keep commit subjects short and imperative; current history uses both prefixed style (`feat: ...`) and milestone style (`Phase 2: ...`).
- Preferred format: `<type>: <summary>` where type is one of `feat`, `fix`, `refactor`, `test`, or `docs`.
- PRs should include a clear summary, linked issue(s), and validation evidence (`pytest`, `ruff check`).
- Include screenshots or terminal captures for UI/TUI changes and note any config/env changes (for example API key setup).
