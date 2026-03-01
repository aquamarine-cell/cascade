"""Provider status display -- delegates to ghost_table."""

from .ghost_table import render_ghost_table


def render_status_table(providers: dict, default_provider: str = "") -> None:
    """Show provider status at startup.

    Backward-compatible wrapper around render_ghost_table.
    """
    render_ghost_table(providers, default_provider)
