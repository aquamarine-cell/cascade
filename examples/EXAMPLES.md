# Cascade CLI Examples

## Setup

First, enable providers in your config:

```bash
# View current config location
cascade config

# Edit config (or copy from examples/config.example.yaml)
nano ~/.config/cascade/config.yaml
```

Set your API keys:
```bash
export GEMINI_API_KEY="sk-..."
export CLAUDE_API_KEY="sk-ant-..."
```

Enable at least one provider in the config file:
```yaml
providers:
  gemini:
    enabled: true  # ← Change this to true
    api_key: ${GEMINI_API_KEY}
    model: gemini-2.0-flash
```

## Single Questions

Ask one-off questions with automatic provider selection:

```bash
# Simple question
cascade ask "What is quantum entanglement?"

# Stream the response in real-time
cascade ask "Write a Python function to sort a list" --stream

# Specify provider
cascade ask "Compare Python and Rust" --provider claude

# With system prompt for context
cascade ask "Explain this code" -s "You are a code reviewer" < file.py
```

## Comparison Mode

Compare how different providers respond to the same question:

```bash
# Compare all enabled providers
cascade compare "Best practices for async Python"

# Compare specific providers
cascade compare "Design a REST API" --providers gemini claude

# Full output displayed side-by-side
cascade compare "Explain neural networks"
```

## Interactive Chat

Have a continuous conversation with a provider:

```bash
# Chat with default provider
cascade chat

# Chat with specific provider
cascade chat --provider claude

# Commands in chat:
#   exit    - Quit the chat
#   quit    - Quit the chat
#   [anything else] - Send as message
```

## File Analysis

Analyze code and other files:

```bash
# Analyze Python file
cascade analyze main.py

# With custom analysis prompt
cascade analyze config.json --prompt "Find security issues"

# Analyze specific file type
cascade analyze data.csv --prompt "Summarize the key insights"

# Use specific provider
cascade analyze legacy.py --provider claude
```

## Real-World Use Cases

### Code Review
```bash
cascade analyze src/main.py --prompt \
  "Review this code for:
   - Performance issues
   - Security vulnerabilities
   - Code style improvements"
```

### Documentation
```bash
cascade ask "Generate Python docstring documentation" \
  --stream < src/util.py
```

### Design Decisions
```bash
cascade compare "Should we use PostgreSQL or MongoDB for this project?" \
  --providers gemini claude
```

### Explaining Unfamiliar Code
```bash
cascade analyze legacy_code.py \
  --system "You are an expert software engineer" \
  --prompt "Explain what this code does in simple terms"
```

### Learning
```bash
cascade ask "Explain RSA encryption step by step"
cascade ask "What are design patterns in Python?"
cascade ask "How does a blockchain work?"
```

### Brainstorming
```bash
cascade chat --provider claude
# Then ask open-ended questions and have a conversation
```

## Tips & Tricks

**Streaming for long responses:**
```bash
cascade ask "Write a complete REST API in Python" --stream
# See output as it generates instead of waiting
```

**Comparing perspectives:**
```bash
cascade compare "What's the best way to learn programming?"
# See how different models approach the question differently
```

**Analyzing multiple files:**
```bash
for file in src/*.py; do
  echo "=== Analyzing $file ==="
  cascade analyze "$file" --prompt "List all functions and their purpose"
done
```

**Batch file analysis:**
```bash
# Create a summary of your codebase
cascade analyze src/ --prompt "Provide an architectural overview"
```

**With pipes:**
```bash
# Generate docstring for clipboard content
cat file.py | cascade ask "Generate a comprehensive docstring" --stream
```

## Advanced

**Environment-based configuration:**
```bash
# Different configs for different environments
export CASCADE_CONFIG=~/.config/cascade/prod.yaml
cascade ask "Deploy instructions"
```

**Provider-specific tuning:**
```yaml
# In config.yaml
providers:
  claude:
    temperature: 0.3  # More deterministic
    max_tokens: 4096  # Longer responses
  
  gemini:
    temperature: 0.9  # More creative
    max_tokens: 2048
```

**Combining with other tools:**
```bash
# Analyze git diff
git diff | cascade ask "Summarize these changes"

# Test code suggestions
cascade ask "Write a unit test for fibonacci" --stream > test.py
python3 -m pytest test.py

# Improve documentation
cascade ask "Improve clarity of this docstring" < old_docs.md
```

## Output Examples

All output uses the Deep Stream theme for beautiful terminal aesthetics.

### Response Panel
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📝 GeminiProvider                                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Quantum entanglement is a phenomenon where two particles become              ┃
┃ connected in such a way that the quantum state of one particle              ┃
┃ instantly influences the state of the other...                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Comparison
Gemini and Claude responses shown side-by-side with cyan and violet borders.

## Troubleshooting

**"Provider 'gemini' not found or not enabled"**
- Check that the provider is enabled in `~/.config/cascade/config.yaml`
- Verify API key environment variable is set: `echo $GEMINI_API_KEY`

**"Error reading config"**
- Ensure `~/.config/cascade/config.yaml` exists and is valid YAML
- Run `cascade config` to see the path and verify it exists

**No response/timeout**
- Check internet connection
- Verify API key is valid for the provider
- Try with `--stream` to see if it's processing

**Want to use a different model?**
- Edit `~/.config/cascade/config.yaml`
- Change the `model` field under the provider
- Check provider docs for available models

## Getting Help

```bash
# See all commands
cascade --help

# Help for specific command
cascade ask --help
cascade compare --help
cascade chat --help
cascade analyze --help
```
