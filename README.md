# ✨ CASCADE

Beautiful multi-model AI code assistant CLI with Deep Stream aesthetics.

**Deep Stream Theme:** Cyan (#00f2ff) × Violet (#7000ff)

## Features

- 🔷 **Multi-Model Support** - Gemini, Claude, with extensible provider system
- 💬 **Multiple Modes** - Single ask, compare, interactive chat, file analysis
- 🎨 **Beautiful UI** - Rich terminal output with Deep Stream color theme
- ⚙️ **Modular Design** - Clean provider interface, plugin system
- 🔧 **Configuration** - YAML-based config at `~/.config/cascade/config.yaml`
- 📦 **Production Ready** - Installable package with entry point

## Installation

```bash
# Clone and install
git clone <repo>
cd cascade
pip install -e .

# Verify
cascade --help
```

## Configuration

First run creates `~/.config/cascade/config.yaml`:

```yaml
providers:
  gemini:
    enabled: true
    api_key: ${GEMINI_API_KEY}
    model: gemini-2.0-flash
    temperature: 0.7
    max_tokens: 2048
  
  claude:
    enabled: true
    api_key: ${CLAUDE_API_KEY}
    model: claude-3-5-sonnet-20241022
    temperature: 0.7
    max_tokens: 2048

defaults:
  provider: gemini
  theme: deep-stream
```

Set environment variables:
```bash
export GEMINI_API_KEY="your-key"
export CLAUDE_API_KEY="your-key"
```

## Usage

### Ask a Question
```bash
cascade ask "explain quantum computing"
cascade ask "write hello world in rust" --stream
cascade ask "analyze this" --system "You are a code reviewer"
```

### Compare Providers
```bash
cascade compare "best practices for async python"
cascade compare "write a function" --providers gemini claude
```

### Interactive Chat
```bash
cascade chat
cascade chat --provider claude
```

### Analyze Files
```bash
cascade analyze main.py
cascade analyze config.json --prompt "Find security issues"
cascade analyze data.csv --provider gemini
```

### View Configuration
```bash
cascade config
```

## Architecture

```
cascade/
├── cascade/
│   ├── __init__.py           # Package exports
│   ├── cli.py                # Click CLI with commands
│   ├── config.py             # YAML configuration
│   ├── providers/
│   │   ├── base.py           # BaseProvider interface
│   │   ├── gemini.py         # Gemini implementation
│   │   └── claude.py         # Claude implementation
│   ├── ui/
│   │   ├── theme.py          # Deep Stream theme colors
│   │   └── output.py         # Rich rendering functions
│   └── plugins/
│       └── file_ops.py       # File operations plugin
├── tests/                    # Test suite
├── setup.py                  # Package configuration
└── README.md                 # This file
```

## Provider System

Extend with new providers by inheriting `BaseProvider`:

```python
from cascade.providers import BaseProvider, ProviderConfig

class MyProvider(BaseProvider):
    def ask(self, prompt, system=None):
        # Implement single prompt
        pass
    
    def stream(self, prompt, system=None):
        # Implement streaming
        pass
    
    def compare(self, prompt, system=None):
        # Return structured data
        pass
```

## Plugin System

FileOpsPlugin included for file operations:

```python
from cascade.plugins import FileOpsPlugin

ops = FileOpsPlugin()
content = ops.read_file("~/myfile.py")
ops.write_file("~/output.txt", "content")
ops.list_files("~/")
ops.append_file("~/log.txt", "new entry")
```

## Color Theme

**Deep Stream:**
- Primary: Cyan `#00f2ff`
- Secondary: Violet `#7000ff`
- Background: `#0a0e27`
- Text: `#e0e0e0`
- Accent: `#00ff88`
- Error: `#ff0055`

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black cascade/ tests/

# Lint
flake8 cascade/ tests/
```

## Library Dependencies

- **click** - CLI framework
- **rich** - Beautiful terminal output
- **pyyaml** - Configuration parsing
- **httpx** - HTTP client for API calls
- **pygments** - Code syntax highlighting

## License

MIT

## Author

Eve

---

Made with 💙 and deep stream aesthetics.
