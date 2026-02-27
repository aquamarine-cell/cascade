"""Interactive REPL mode for Cascade - the main entry point."""

import readline
import sys
from typing import Optional
from .cli import CascadeApp
from .ui.theme import console, CYAN, VIOLET
from .utils.time import formatted_time, get_timezone


class CascadeREPL:
    """Interactive REPL interface for Cascade."""

    def __init__(self, app: CascadeApp):
        """Initialize REPL with app instance."""
        self.app = app
        self.history = []
        self.current_provider = app.config.get_default_provider()

    def welcome(self):
        """Show welcome message."""
        console.print(
            f"\n[{CYAN}✨ CASCADE{CYAN}][/] Multi-model AI Assistant\n",
            style=f"bold {CYAN}"
        )
        console.print(f"Time: {formatted_time(tz=get_timezone())}", style="dim")
        console.print(f"Default provider: {self.current_provider}", style="dim")
        console.print("\nCommands:", style=f"bold {VIOLET}")
        console.print("  /providers    - List available providers")
        console.print("  /switch <name> - Switch default provider")
        console.print("  /time         - Show current time")
        console.print("  /help         - Show this help")
        console.print("  /exit, /quit  - Exit CASCADE")
        console.print("\nOtherwise, just type your question!\n", style="dim")

    def list_providers(self):
        """Show available providers."""
        console.print("\nAvailable providers:", style=f"bold {CYAN}")
        for name in self.app.providers.keys():
            status = "●" if name == self.current_provider else "○"
            console.print(f"  {status} {name}")
        console.print()

    def switch_provider(self, name: str):
        """Switch to a different provider."""
        if name not in self.app.providers:
            console.print(f"Provider '{name}' not found.", style="dim red")
            self.list_providers()
            return
        
        self.current_provider = name
        console.print(f"Switched to {name}", style=f"dim {CYAN}")

    def handle_command(self, line: str) -> bool:
        """Handle special commands. Returns True to continue, False to exit."""
        if not line.startswith("/"):
            return True

        cmd = line.strip("/").lower()

        if cmd in ["exit", "quit"]:
            console.print("Goodbye! 🌊", style=f"dim {VIOLET}")
            return False

        elif cmd == "providers":
            self.list_providers()

        elif cmd.startswith("switch "):
            provider_name = cmd.split(" ", 1)[1].strip()
            self.switch_provider(provider_name)

        elif cmd == "time":
            console.print(f"Time: {formatted_time(tz=get_timezone())}", style="dim")

        elif cmd == "help":
            self.welcome()

        else:
            console.print(f"Unknown command: /{cmd}", style="dim red")

        return True

    def run(self):
        """Start the REPL loop."""
        self.welcome()

        try:
            while True:
                try:
                    # Get user input
                    prompt = f"[{self.current_provider}] > "
                    line = input(prompt)

                    if not line.strip():
                        continue

                    # Handle commands
                    if not self.handle_command(line):
                        break

                    # If it's a regular prompt, send to provider
                    if not line.startswith("/"):
                        try:
                            response = self.app.ask(line, provider=self.current_provider)
                            self.history.append({"prompt": line, "response": response})
                        except Exception as e:
                            console.print(f"Error: {e}", style="dim red")

                except KeyboardInterrupt:
                    console.print("\n")
                    continue

        except EOFError:
            console.print("\nGoodbye! 🌊", style=f"dim {VIOLET}")


def main():
    """Entry point for `cascade` command."""
    app = CascadeApp()
    repl = CascadeREPL(app)
    repl.run()


if __name__ == "__main__":
    main()
