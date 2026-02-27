"""Cascade CLI - Beautiful multi-model AI assistant."""

import click
import sys
from typing import Optional

from .config import ConfigManager
from .providers import GeminiProvider, ClaudeProvider
from .ui import render_header, render_footer, render_response, render_comparison
from .ui.output import render_error, stream_response
from .ui.theme import console, CYAN, VIOLET
from .plugins import FileOpsPlugin


class CascadeApp:
    """Main Cascade application."""

    def __init__(self):
        self.config = ConfigManager()
        self.providers = {}
        self._init_providers()
        self.file_ops = FileOpsPlugin()

    def _init_providers(self) -> None:
        """Initialize enabled providers."""
        provider_classes = {
            "gemini": GeminiProvider,
            "claude": ClaudeProvider,
        }
        
        for provider_name, provider_class in provider_classes.items():
            config = self.config.get_provider_config(provider_name)
            if config:
                try:
                    self.providers[provider_name] = provider_class(config)
                except Exception as e:
                    console.print(f"Failed to initialize {provider_name}: {e}", style="dim red")

    def get_provider(self, name: Optional[str] = None):
        """Get a provider by name or default."""
        provider_name = name or self.config.get_default_provider()
        
        if provider_name not in self.providers:
            raise click.ClickException(
                f"Provider '{provider_name}' not found or not enabled. "
                f"Available: {list(self.providers.keys())}"
            )
        
        return self.providers[provider_name]

    def ask(self, prompt: str, provider: Optional[str] = None, system: Optional[str] = None, stream: bool = False) -> str:
        """Ask a single question."""
        prov = self.get_provider(provider)
        
        if stream:
            return stream_response(prov.stream(prompt, system), prov.name)
        else:
            response = prov.ask(prompt, system)
            render_response(response, provider=prov.name)
            return response

    def compare(self, prompt: str, providers: Optional[list[str]] = None) -> list[dict]:
        """Compare responses from multiple providers."""
        provider_names = providers or list(self.providers.keys())
        
        if not provider_names:
            raise click.ClickException("No providers available for comparison")
        
        results = []
        for provider_name in provider_names:
            if provider_name not in self.providers:
                continue
            
            prov = self.providers[provider_name]
            response = prov.compare(prompt)
            results.append(response)
        
        render_comparison(results)
        return results

    def chat(self, provider: Optional[str] = None) -> None:
        """Interactive chat mode."""
        prov = self.get_provider(provider)
        render_header("CASCADE CHAT", f"Model: {prov.config.model}")
        console.print("\nType 'quit' or 'exit' to leave\n", style=f"dim {CYAN}")
        
        messages = []
        
        try:
            while True:
                prompt = click.prompt(f"[{prov.name}]", default="", show_default=False)
                
                if prompt.lower() in ["quit", "exit"]:
                    console.print("Goodbye!", style=f"dim {VIOLET}")
                    break
                
                if not prompt.strip():
                    continue
                
                response = prov.ask(prompt)
                render_response(response, provider=prov.name)
                messages.append({"prompt": prompt, "response": response})
        except KeyboardInterrupt:
            console.print("\n\nInterrupted.", style="dim red")

    def analyze(self, file_path: str, prompt: Optional[str] = None, provider: Optional[str] = None) -> str:
        """Analyze a file with AI."""
        # Read file
        content = self.file_ops.read_file(file_path)
        if content.startswith("Error"):
            raise click.ClickException(content)
        
        # Build analysis prompt
        analysis_prompt = prompt or "Analyze this code and provide insights:"
        full_prompt = f"{analysis_prompt}\n\n```\n{content}\n```"
        
        prov = self.get_provider(provider)
        response = prov.ask(full_prompt)
        render_response(response, provider=prov.name)
        
        return response


# Global app instance
_app = None

def get_app() -> CascadeApp:
    """Get or create the app instance."""
    global _app
    if _app is None:
        _app = CascadeApp()
    return _app


# CLI Commands
@click.group()
def cli():
    """
    ✨ CASCADE - Beautiful multi-model AI assistant
    
    Ask questions, compare providers, chat interactively, analyze files.
    """
    pass


@cli.command()
@click.argument("prompt", nargs=-1, required=True)
@click.option("--provider", "-p", help="Provider to use (gemini, claude)")
@click.option("--system", "-s", help="System prompt")
@click.option("--stream", is_flag=True, help="Stream response in real-time")
def ask(prompt, provider, system, stream):
    """Ask a single question."""
    app = get_app()
    prompt_text = " ".join(prompt)
    try:
        app.ask(prompt_text, provider=provider, system=system, stream=stream)
    except click.ClickException:
        raise
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


@cli.command()
@click.argument("prompt", nargs=-1, required=True)
@click.option("--providers", "-p", multiple=True, help="Providers to compare")
def compare(prompt, providers):
    """Compare responses from multiple providers."""
    app = get_app()
    prompt_text = " ".join(prompt)
    try:
        app.compare(prompt_text, providers=list(providers) if providers else None)
    except click.ClickException:
        raise
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


@cli.command()
@click.option("--provider", "-p", help="Provider to use")
def chat(provider):
    """Start interactive chat mode."""
    app = get_app()
    try:
        app.chat(provider=provider)
    except click.ClickException:
        raise
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


@cli.command()
@click.argument("file_path")
@click.option("--prompt", "-p", help="Custom analysis prompt")
@click.option("--provider", "-pr", help="Provider to use")
def analyze(file_path, prompt, provider):
    """Analyze a file with AI."""
    app = get_app()
    try:
        app.analyze(file_path, prompt=prompt, provider=provider)
    except click.ClickException:
        raise
    except Exception as e:
        render_error(str(e))
        sys.exit(1)


@cli.command()
def config():
    """Show configuration."""
    app = get_app()
    config_path = app.config.config_path
    
    console.print(f"Config file: {config_path}")
    console.print(f"Enabled providers: {app.config.get_enabled_providers()}")
    console.print(f"Default provider: {app.config.get_default_provider()}")


if __name__ == "__main__":
    cli()
