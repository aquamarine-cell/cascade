"""Borderless ghost table for provider roster at startup."""

from rich.text import Text
from .theme import console, DEFAULT_THEME, CascadeTheme


def render_ghost_table(
    providers: dict,
    default_provider: str = "",
    theme: CascadeTheme = DEFAULT_THEME,
) -> None:
    """Render a borderless, whitespace-aligned provider table.

    Active row uses provider accent color; inactive rows are barely visible.
    """
    palette = theme.palette
    col_provider = 14
    col_model = 29

    # Header -- uppercase, muted
    header = Text()
    header.append("  ")
    header.append("PROVIDER".ljust(col_provider), style=f"dim {palette.text_muted}")
    header.append("MODEL".ljust(col_model), style=f"dim {palette.text_muted}")
    header.append("STATUS", style=f"dim {palette.text_muted}")
    console.print(header)

    if not providers:
        line = Text()
        line.append("  ")
        line.append("(none)".ljust(col_provider), style=f"dim {palette.text_muted}")
        line.append("-".ljust(col_model), style=f"dim {palette.text_muted}")
        line.append("no providers configured", style=f"dim {palette.error}")
        console.print(line)
        console.print()
        return

    for name in sorted(providers.keys()):
        prov = providers[name]
        model = prov.config.model if hasattr(prov, "config") else "?"
        is_active = name == default_provider
        pt = theme.get_provider(name)

        line = Text()
        line.append("  ")

        if is_active:
            line.append(name.ljust(col_provider), style=f"bold {pt.accent}")
            line.append(model.ljust(col_model), style=f"{palette.text_bright}")
            line.append("active", style=f"{pt.accent}")
        else:
            # Barely visible -- text_muted + dim
            muted = palette.text_muted
            line.append(name.ljust(col_provider), style=f"dim {muted}")
            line.append(model.ljust(col_model), style=f"dim {muted}")
            line.append("\u00b7", style=f"dim {muted}")

        console.print(line)

    console.print()
