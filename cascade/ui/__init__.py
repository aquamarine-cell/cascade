"""Terminal UI components with Deep Stream theme."""

from .theme import THEME, render_header, render_footer
from .output import render_response, render_comparison, render_thinking, render_error
from .banner import render_banner
from .status import render_status_table
from .mode import ModeState, MODE_ORDER
from .gutter import render_gutter_line, render_user_gutter, render_response_block, render_bookmark, GUTTER_WIDTH
from .markdown import render_markdown_line
from .code_block import render_code_container
from .spinner import GutterSpinner
from .input_container import print_input_top, print_input_bottom, build_prompt_prefix, print_mode_indicator
from .statusbar import build_status_bar
from .odometer import render_exit_summary
from .stream import StreamRenderer

__all__ = [
    "THEME",
    "render_header",
    "render_footer",
    "render_response",
    "render_comparison",
    "render_thinking",
    "render_error",
    "render_banner",
    "render_status_table",
    "ModeState",
    "MODE_ORDER",
    "render_gutter_line",
    "render_user_gutter",
    "render_response_block",
    "render_bookmark",
    "GUTTER_WIDTH",
    "render_markdown_line",
    "render_code_container",
    "GutterSpinner",
    "print_input_top",
    "print_input_bottom",
    "build_prompt_prefix",
    "print_mode_indicator",
    "build_status_bar",
    "render_exit_summary",
    "StreamRenderer",
]
