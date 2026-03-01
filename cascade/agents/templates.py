"""Project-type templates for the /init wizard.

Each template provides scaffolding content for a .cascade/ project directory:
system_prompt, agents, workflows, and verify commands.
"""

from pathlib import Path


# -- Templates ----------------------------------------------------------------

_TEMPLATES: dict[str, dict] = {
    "python": {
        "system_prompt": (
            "You are a Python development assistant.\n"
            "Follow PEP 8, use type hints, prefer immutability.\n"
            "Run ruff for linting, pytest for tests, mypy for type checking."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a code reviewer. Check for bugs, style, and security.",
            },
            "security": {
                "provider": "{{default}}",
                "system_prompt": "You are a security auditor. Find vulnerabilities and suggest fixes.",
            },
        },
        "workflows": {
            "review-and-fix": {
                "steps": ["reviewer", "planner"],
                "description": "Review code then plan fixes",
            },
        },
        "verify": {
            "lint": "ruff check .",
            "test": "python -m pytest -x -q",
            "typecheck": "mypy .",
        },
    },
    "web": {
        "system_prompt": (
            "You are a web development assistant.\n"
            "Follow modern JS/TS best practices.\n"
            "Use ESLint for linting, vitest or jest for tests."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a code reviewer. Check for bugs, style, and accessibility.",
            },
            "accessibility": {
                "provider": "{{default}}",
                "system_prompt": "You are an accessibility auditor. Check WCAG compliance.",
            },
        },
        "workflows": {
            "review-and-fix": {
                "steps": ["reviewer", "planner"],
                "description": "Review code then plan fixes",
            },
        },
        "verify": {
            "lint": "npx eslint .",
            "test": "npx vitest run",
            "build": "npm run build",
        },
    },
    "api": {
        "system_prompt": (
            "You are an API development assistant.\n"
            "Follow REST best practices, validate inputs, handle errors.\n"
            "Run linting, tests, and security audits."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a code reviewer. Check for bugs, style, and security.",
            },
            "security": {
                "provider": "{{default}}",
                "system_prompt": "You are a security auditor. Find injection, auth, and data-leak vulnerabilities.",
            },
        },
        "workflows": {
            "secure-review": {
                "steps": ["security", "reviewer"],
                "description": "Security audit then code review",
            },
        },
        "verify": {
            "lint": "ruff check . || npx eslint .",
            "test": "python -m pytest -x -q || npx vitest run",
            "security": "bandit -r . || npm audit",
        },
    },
    "rust": {
        "system_prompt": (
            "You are a Rust development assistant.\n"
            "Follow idiomatic Rust, prefer safe code, handle errors with Result.\n"
            "Use cargo check, cargo test, and clippy."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a Rust code reviewer. Check for safety, idiomatic patterns, and performance.",
            },
        },
        "workflows": {
            "review-and-fix": {
                "steps": ["reviewer", "planner"],
                "description": "Review code then plan fixes",
            },
        },
        "verify": {
            "lint": "cargo clippy -- -D warnings",
            "test": "cargo test",
            "build": "cargo check",
        },
    },
    "go": {
        "system_prompt": (
            "You are a Go development assistant.\n"
            "Follow idiomatic Go, handle errors explicitly, use interfaces.\n"
            "Use go vet and go test."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a Go code reviewer. Check for idiomatic patterns, error handling, and concurrency safety.",
            },
        },
        "workflows": {
            "review-and-fix": {
                "steps": ["reviewer", "planner"],
                "description": "Review code then plan fixes",
            },
        },
        "verify": {
            "lint": "go vet ./...",
            "test": "go test ./...",
            "build": "go build ./...",
        },
    },
    "general": {
        "system_prompt": (
            "You are a development assistant.\n"
            "Follow project conventions, write clean code, and test your changes."
        ),
        "agents": {
            "planner": {
                "provider": "{{default}}",
                "system_prompt": "You are a planning agent. Break tasks into steps.",
            },
            "reviewer": {
                "provider": "{{default}}",
                "system_prompt": "You are a code reviewer. Check for bugs, style, and maintainability.",
            },
        },
        "workflows": {
            "review-and-fix": {
                "steps": ["reviewer", "planner"],
                "description": "Review code then plan fixes",
            },
        },
        "verify": {
            "lint": "echo 'configure lint command'",
            "test": "echo 'configure test command'",
        },
    },
}

PROJECT_TYPES: tuple[str, ...] = tuple(sorted(_TEMPLATES.keys()))


def detect_project_type(path: Path) -> str:
    """Detect the project type by scanning for well-known config files.

    Returns one of the PROJECT_TYPES strings.
    """
    path = path.resolve()

    # Python
    if (path / "pyproject.toml").is_file() or (path / "setup.py").is_file():
        return "python"

    # Rust
    if (path / "Cargo.toml").is_file():
        return "rust"

    # Go
    if (path / "go.mod").is_file():
        return "go"

    # Web / JS/TS
    if (path / "package.json").is_file():
        return "web"

    return "general"


def get_template(project_type: str) -> dict:
    """Return the template dict for a project type.

    Falls back to 'general' if the type is unknown.
    """
    return _TEMPLATES.get(project_type, _TEMPLATES["general"])
