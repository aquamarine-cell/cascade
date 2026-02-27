# Development Guide - Cascade

## Project Structure

```
cascade/
├── cascade/                    # Main package
│   ├── __init__.py            # Package exports
│   ├── cli.py                 # Click CLI with commands (7.1 KB)
│   ├── config.py              # YAML configuration management (3.7 KB)
│   ├── providers/             # AI provider implementations
│   │   ├── base.py            # BaseProvider abstract class (1.2 KB)
│   │   ├── gemini.py          # Google Gemini API (3.2 KB)
│   │   └── claude.py          # Anthropic Claude API (2.6 KB)
│   ├── ui/                    # Terminal UI components
│   │   ├── theme.py           # Deep Stream color theme (1.2 KB)
│   │   └── output.py          # Rich rendering functions (3.9 KB)
│   └── plugins/               # Extensible plugin system
│       └── file_ops.py        # File operations plugin (1.5 KB)
├── tests/                     # Test suite (12 tests, all passing)
│   ├── test_config.py
│   ├── test_plugins.py
│   └── test_providers.py
├── setup.py                   # Package configuration
├── README.md                  # User documentation
└── DEVELOPMENT.md             # This file
```

**Total:** 685 lines of production code + tests + docs

## Architecture

### Provider System

All AI providers extend `BaseProvider`:

```python
class BaseProvider(ABC):
    def ask(self, prompt, system=None) -> str
    def stream(self, prompt, system=None) -> Iterator[str]
    def compare(self, prompt, system=None) -> dict
```

Current implementations:
- **GeminiProvider** - Google Gemini API with streaming
- **ClaudeProvider** - Anthropic Claude API with streaming

Adding new providers is simple — implement the 3 methods.

### CLI Commands

Implemented via Click with proper error handling:

1. **ask** - Single prompt with optional streaming
2. **compare** - Compare multiple provider responses side-by-side
3. **chat** - Interactive conversation mode
4. **analyze** - AI analysis of files
5. **config** - View configuration

### Configuration

YAML-based at `~/.config/cascade/config.yaml`:
- Per-provider settings (model, temperature, max_tokens)
- Environment variable substitution (${VAR_NAME})
- Default provider selection

### UI Theming

Deep Stream colors consistently applied:
- **Cyan #00f2ff** - Primary, responses
- **Violet #7000ff** - Secondary, thinking/analysis
- **#00ff88** - Accent highlights
- **#ff0055** - Error states

Using Rich library for:
- Beautiful panels and borders
- Syntax highlighting for code
- Real-time streaming output
- Side-by-side comparisons

## Testing

All 12 tests pass. Three test modules:

**test_config.py:**
- Config file creation
- Default provider resolution
- Environment variable expansion

**test_plugins.py:**
- File write/read
- File append
- Directory listing

**test_providers.py:**
- Provider config creation
- BaseProvider interface
- Mock provider implementation

Run tests:
```bash
python3 -m pytest tests/ -v
```

## Making Changes

### Adding a New Provider

1. Create `cascade/providers/myprovider.py`
2. Inherit from `BaseProvider`
3. Implement `ask()`, `stream()`, `compare()`
4. Register in `cascade/providers/__init__.py`
5. Add to config defaults

Example:
```python
from .base import BaseProvider, ProviderConfig

class MyProvider(BaseProvider):
    def ask(self, prompt, system=None):
        # Implementation
        pass
    
    def stream(self, prompt, system=None):
        # Implement streaming
        pass
    
    def compare(self, prompt, system=None):
        return {"provider": self.name, "response": "..."}
```

### Adding a Plugin

1. Create `cascade/plugins/myplugin.py`
2. Implement static methods for operations
3. Register in `cascade/plugins/__init__.py`
4. Use in CLI via `CascadeApp`

### Extending the CLI

Add commands to `cascade/cli.py`:

```python
@cli.command()
@click.argument("arg")
@click.option("--opt", help="Option")
def mycommand(arg, opt):
    """Command description."""
    app = get_app()
    # Use app.providers, app.config, app.file_ops
```

## Dependencies

Minimal, production-grade libraries:

```
click>=8.0          # CLI framework
rich>=13.0          # Beautiful terminal output
pyyaml>=6.0         # Config parsing
httpx>=0.24.0       # HTTP client (async-capable)
pygments>=2.14.0    # Code syntax highlighting
```

## Performance Notes

- **Streaming** - Implemented with async-capable httpx
- **Memory** - Configuration cached, minimal overhead
- **Latency** - Passes through API latency, no additional delays
- **Startup** - ~50ms before first API call

## Design Decisions

1. **YAML over JSON** - Human-editable config
2. **Single config file** - Simpler than per-provider configs
3. **BaseProvider ABC** - Enforces interface consistency
4. **Plugin system** - Room for expansion without bloating core
5. **Rich for UI** - Terminal experience over web UI
6. **Click for CLI** - Industry standard, great DX
7. **No async/await** - Keep it simple, APIs handle concurrency
8. **httpx over requests** - Modern, better streaming support

## Future Enhancements (Phase 2+)

- [ ] Ollama local provider
- [ ] Together AI provider
- [ ] Qwen provider
- [ ] Conversation history/memory
- [ ] Prompt templates
- [ ] Export to Markdown
- [ ] Batch operations
- [ ] Performance benchmarking
- [ ] Custom color themes
- [ ] Shell integration (!!cascade)
