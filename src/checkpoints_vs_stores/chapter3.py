"""Chapter 3 CLI: human-in-the-loop and time travel.

The two remaining checkpoint-powered patterns from the official docs'
canonical four: pausing a graph for a human decision (``interrupt()``), and
replaying or forking a thread's checkpoint history.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from checkpoints_vs_stores.demo import MIN_SIDE_BY_SIDE_WIDTH, strip_heading
from checkpoints_vs_stores.hitl_demo import format_hitl_story, run_hitl_story
from checkpoints_vs_stores.timetravel_demo import format_timetravel_story, run_timetravel_story
from checkpoints_vs_stores.utils import compact_json

SECTIONS = {
    "hitl": ("Human-in-the-loop - interrupt()", "cyan", format_hitl_story),
    "timetravel": ("Time travel - replay & fork", "magenta", format_timetravel_story),
}

RULES = (
    "interrupt() needs a checkpointer and a thread_id - use a durable checkpointer in production",
    "a paused interrupt waits indefinitely, and the pause survives process restarts",
    "resume re-executes the interrupted node from its start: keep its side effects idempotent",
    "time travel: nodes before the checkpoint are not re-run; nodes after re-execute (LLMs too)",
    "forks stay in the thread's checkpoint history - an audit trail of every timeline",
)


def collect(command: str) -> dict[str, Any]:
    """Run one or more chapter 3 demos and return a dictionary of results."""

    if command == "hitl":
        return {"hitl": run_hitl_story()}
    if command == "timetravel":
        return {"timetravel": run_timetravel_story()}
    if command == "all":
        return {"hitl": run_hitl_story(), "timetravel": run_timetravel_story()}
    raise ValueError(f"Unsupported chapter 3 command: {command}")


def render_text(results: dict[str, Any]) -> str:
    """Render collected results as plain text."""

    sections = [SECTIONS[key][2](story) for key, story in results.items()]
    return "\n\n" + "\n\n".join(sections)


def build_panel(key: str, story: dict[str, Any]) -> Panel:
    """Wrap one demo's formatted output in a titled, colored frame."""

    title, border, formatter = SECTIONS[key]
    body = Text(strip_heading(formatter(story)))
    body.highlight_regex(r"(?m)^Lesson: .+$", "bold")
    return Panel(body, title=f"[bold]{title}[/bold]", border_style=border, padding=(1, 2))


def build_rules_panel() -> Panel:
    """The docs-verified rules that make these patterns safe in production."""

    body = Text("\n".join(f"* {rule}" for rule in RULES))
    return Panel(
        body,
        title="[bold]Rules of the road[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


def render_tui(console: Console, results: dict[str, Any]) -> None:
    """Framed panels: hitl | timetravel side by side, rules below."""

    pair = [build_panel(key, results[key]) for key in ("hitl", "timetravel") if key in results]
    if len(pair) == 2 and console.width >= MIN_SIDE_BY_SIDE_WIDTH:
        half = console.width // 2
        options = console.options.update_width(half)
        tallest = max(len(console.render_lines(panel, options, pad=False)) for panel in pair)
        for panel in pair:
            panel.height = tallest
        grid = Table.grid()
        grid.add_column(width=half)
        grid.add_column(width=half)
        grid.add_row(*pair)
        console.print(grid)
    else:
        for panel in pair:
            console.print(panel)

    console.print(build_rules_panel())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lg-memory-demo3",
        description="Chapter 3: human-in-the-loop and time travel on checkpoints.",
    )
    parser.add_argument(
        "demo",
        choices=["hitl", "timetravel", "all"],
        help="Which demo to run.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of formatted text.")
    parser.add_argument(
        "--plain", action="store_true", help="Print flat text instead of the panel TUI."
    )
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = collect(args.demo)

    if args.json:
        print(compact_json(results))
        return 0

    if args.plain:
        print(render_text(results))
        return 0

    console = Console(color_system=None if args.no_color else "auto")
    console.print(
        Panel.fit(
            "[bold]Chapter 3: human-in-the-loop & time travel[/bold]\n"
            "Checkpoints make agents pausable, resumable, and forkable.",
            title="checkpoints-vs-stores",
            border_style="cyan",
        )
    )
    render_tui(console, results)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
