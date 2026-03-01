"""Main chat screen for the Cascade TUI.

Composes WelcomeHeader + ChatHistory + InputFrame + StatusBar.
Bridges to synchronous provider.stream() via run_worker(thread=True).
"""

import datetime

from rich.text import Text
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Input, Static

from ..widgets.header import WelcomeHeader, ProviderGhostTable
from ..widgets.message import ChatHistory, MessageWidget, ThinkingIndicator
from ..widgets.input_frame import InputFrame
from ..widgets.status_bar import StatusBar
from ..widgets.stream_message import StreamMessage
from ..theme import PALETTE, MODE_CYCLE, MODES
from ..commands import CommandHandler


def summarize_user_prompt(prompt: str) -> str:
    """Return a compact display string for pasted multi-line content."""
    line_count = prompt.count("\n") + 1
    if line_count >= 2:
        return f"[pasted content 1 + {line_count - 1} lines]"
    return prompt


class MainScreen(Screen):
    """The core chat interface."""

    BINDINGS = [
        ("shift+tab", "cycle_mode", "Cycle Mode"),
        ("ctrl+c", "exit_app", "Exit"),
        ("ctrl+d", "exit_app", "Exit"),
        ("escape", "blur_input", "Focus Chat"),
    ]

    def __init__(
        self,
        active_provider: str = "gemini",
        mode: str = "design",
        providers: dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._active_provider = active_provider
        self._mode = mode
        self._providers = providers or {}
        self._header_visible = True
        self._cmd_handler: CommandHandler | None = None
        self._thinking: ThinkingIndicator | None = None

    def compose(self) -> ComposeResult:
        yield WelcomeHeader(
            active_provider=self._active_provider,
            providers=self._providers,
        )
        yield ChatHistory()
        yield InputFrame(
            active_provider=self._active_provider,
            mode=self._mode,
        )
        yield StatusBar(
            provider_tokens=dict(self.app.state.provider_tokens),
        )

    def on_mount(self) -> None:
        try:
            self.query_one("#main_input").focus()
        except Exception:
            pass
        self._cmd_handler = CommandHandler(self.app)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        prompt = event.value.strip()
        if not prompt:
            return

        # Clear input
        event.input.value = ""

        # Slash commands
        if self._cmd_handler and self._cmd_handler.is_command(prompt):
            self._cmd_handler.handle(prompt)
            return

        # Hide welcome header on first real message
        if self._header_visible:
            self._header_visible = False
            try:
                self.query_one(WelcomeHeader).display = False
            except Exception:
                pass

        # Record user message in state + history DB
        self.app.state.add_message("you", prompt)
        self.app.record_message("user", prompt)

        # Mount user message widget
        chat = self.query_one(ChatHistory)
        chat.mount(MessageWidget("you", summarize_user_prompt(prompt)))
        chat.scroll_end(animate=False)

        # Kick off provider response in a worker thread
        self._send_to_provider(prompt)

    # ------------------------------------------------------------------
    # Provider streaming bridge
    # ------------------------------------------------------------------

    def _send_to_provider(self, prompt: str) -> None:
        """Start a background worker that calls the synchronous provider."""
        chat = self.query_one(ChatHistory)

        # Show thinking spinner
        self._thinking = ThinkingIndicator(self._active_provider)
        chat.mount(self._thinking)
        chat.scroll_end(animate=False)
        self.app.state.set_thinking(self._active_provider, True)

        # Mount a StreamMessage that will accumulate chunks
        self._stream_msg = StreamMessage(self._active_provider)
        chat.mount(self._stream_msg)

        provider_name = self._active_provider
        def _worker() -> None:
            self._provider_worker(prompt, provider_name)

        self.run_worker(
            _worker,
            thread=True,
            exclusive=True,
        )

    def _provider_worker(self, prompt: str, provider_name: str):
        """Run in a worker thread -- calls synchronous provider.stream()."""
        cli_app = self.app.cli_app
        if cli_app is None:
            self.app.call_from_thread(self._on_stream_error, "No CLI app available")
            return

        prov = cli_app.providers.get(provider_name)
        if prov is None:
            self.app.call_from_thread(
                self._on_stream_error, f"Provider '{provider_name}' not available",
            )
            return

        # Build system prompt
        pipeline = cli_app.prompt_pipeline
        if cli_app.context_builder.source_count > 0:
            from ..prompts.layers import PRIORITY_REPL_CONTEXT
            upload_ctx = cli_app.context_builder.build()
            pipeline = pipeline.add_layer(
                "upload_context", upload_ctx, PRIORITY_REPL_CONTEXT,
            )
        final_system = pipeline.build() or None

        # Run hooks
        from ..hooks import HookEvent
        cli_app.hook_runner.run_hooks(HookEvent.BEFORE_ASK, context={
            "prompt": prompt,
            "provider": provider_name,
        })

        full_response = []
        try:
            for chunk in prov.stream(prompt, final_system):
                full_response.append(chunk)
                self.app.call_from_thread(self._on_stream_chunk, chunk)

            response_text = "".join(full_response)

            # Get usage
            usage = prov.last_usage or (0, 0)
            self.app.call_from_thread(
                self._on_stream_done, provider_name, response_text, usage[0], usage[1],
            )

            # Run after hooks
            cli_app.hook_runner.run_hooks(HookEvent.AFTER_RESPONSE, context={
                "response_length": str(len(response_text)),
                "provider": provider_name,
                "tool_calls": "0",
            })

        except Exception as e:
            self.app.call_from_thread(self._on_stream_error, str(e))

    def _on_stream_chunk(self, chunk: str) -> None:
        """Called from worker thread via app.call_from_thread."""
        if hasattr(self, "_stream_msg"):
            self._stream_msg.feed(chunk)
            chat = self.query_one(ChatHistory)
            chat.scroll_end(animate=False)

    def _on_stream_done(
        self, provider: str, full_text: str, input_tokens: int, output_tokens: int,
    ) -> None:
        """Called when streaming is complete."""
        # Remove thinking indicator
        if self._thinking:
            self._thinking.remove()
            self._thinking = None
        self.app.state.set_thinking(provider, False)

        # Finalize the stream message
        if hasattr(self, "_stream_msg"):
            self._stream_msg.finish()

        # Record in state + history DB
        total = input_tokens + output_tokens
        self.app.state.add_message(provider, full_text, tokens=total)
        self.app.state.update_tokens(provider, input_tokens, output_tokens)
        self.app.record_message("assistant", full_text, token_count=total)

        # Update status bar
        try:
            self.query_one(StatusBar).update_tokens(self.app.state.provider_tokens)
        except Exception:
            pass

        # Update input frame token count
        try:
            self.query_one(InputFrame).token_count = self.app.state.total_tokens
        except Exception:
            pass

    def _on_stream_error(self, error_msg: str) -> None:
        """Called when streaming fails."""
        if self._thinking:
            self._thinking.remove()
            self._thinking = None
        self.app.state.set_thinking(self._active_provider, False)

        chat = self.query_one(ChatHistory)
        chat.mount(MessageWidget("system", f"Error: {error_msg}"))
        chat.scroll_end(animate=False)

    # ------------------------------------------------------------------
    # Mode cycling
    # ------------------------------------------------------------------

    def action_cycle_mode(self) -> None:
        current_idx = MODE_CYCLE.index(self._mode)
        next_idx = (current_idx + 1) % len(MODE_CYCLE)
        self._mode = MODE_CYCLE[next_idx]
        self._active_provider = MODES[self._mode]["provider"]

        # Update state
        self.app.state.set_provider(self._active_provider, self._mode)

        # Update widgets
        try:
            inp = self.query_one(InputFrame)
            inp.active_provider = self._active_provider
            inp.mode = self._mode
        except Exception:
            pass

        try:
            self.query_one(ProviderGhostTable).set_active(self._active_provider)
        except Exception:
            pass

        # Insert bookmark separator
        chat = self.query_one(ChatHistory)
        now = datetime.datetime.now().strftime("%I:%M %p")
        sep_text = Text(
            f"\u2500\u2500\u2500 {now} . switching to {self._mode} mode \u2500\u2500\u2500",
            style=f"dim {PALETTE.text_dim}",
        )
        sep = Static(sep_text, classes="bookmark")
        chat.mount(sep)
        chat.scroll_end(animate=False)

    # ------------------------------------------------------------------
    # Exit
    # ------------------------------------------------------------------

    def action_exit_app(self) -> None:
        from .exit import ExitScreen

        elapsed = self.app.state.elapsed
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        uptime = f"{minutes:02d}:{seconds:02d}"

        self.app.push_screen(ExitScreen(
            session_id=self.app.state.session_id,
            uptime=uptime,
            messages_sent=self.app.state.message_count,
            messages_received=self.app.state.response_count,
            tokens=dict(self.app.state.provider_tokens),
        ))

    def action_blur_input(self) -> None:
        try:
            self.query_one("#main_input").blur()
            self.query_one(ChatHistory).focus()
        except Exception:
            pass
