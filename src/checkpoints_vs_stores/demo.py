"""Command-line interface for the LangGraph persistence demos."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from checkpoints_vs_stores.checkpoint_demo import (
    format_checkpoint_story,
    run_checkpoint_story,
)
from checkpoints_vs_stores.combined_demo import format_combined_story, run_combined_story
from checkpoints_vs_stores.store_demo import format_store_story, run_store_story
from checkpoints_vs_stores.utils import compact_json

SECTIONS = {
    "checkpoint": ("Checkpoints - thread-scoped", "cyan", format_checkpoint_story),
    "store": ("Stores - cross-thread", "magenta", format_store_story),
    "combined": ("Combined - both layers", "green", format_combined_story),
}

# Below this console width, side-by-side panels wrap too aggressively to read.
MIN_SIDE_BY_SIDE_WIDTH = 100


def collect(command: str) -> dict[str, Any]:
    """Run one or more demos and return a dictionary of results."""

    if command == "checkpoint":
        return {"checkpoint": run_checkpoint_story()}
    if command == "store":
        return {"store": run_store_story()}
    if command in {"both", "combined"}:
        return {"combined": run_combined_story()}
    if command == "all":
        return {
            "checkpoint": run_checkpoint_story(),
            "store": run_store_story(),
            "combined": run_combined_story(),
        }
    raise ValueError(f"Unsupported demo command: {command}")


def render_text(results: dict[str, Any]) -> str:
    """Render collected results as plain text."""

    sections: list[str] = []
    if "checkpoint" in results:
        sections.append(format_checkpoint_story(results["checkpoint"]))
    if "store" in results:
        sections.append(format_store_story(results["store"]))
    if "combined" in results:
        sections.append(format_combined_story(results["combined"]))
    return "\n\n" + "\n\n".join(sections)


def strip_heading(formatted: str) -> str:
    """Drop the leading `# ...` line; the panel title carries it in the TUI."""

    lines = formatted.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines)


def build_panel(key: str, story: dict[str, Any]) -> Panel:
    """Wrap one demo's formatted output in a titled, colored frame."""

    title, border, formatter = SECTIONS[key]
    body = Text(strip_heading(formatter(story)))
    body.highlight_regex(r"(?m)^Lesson: .+$", "bold")
    return Panel(body, title=f"[bold]{title}[/bold]", border_style=border, padding=(1, 2))


def build_decision_tree() -> Panel:
    """A small decision tree: which persistence layer does my agent need?"""

    tree = Tree("[bold]What should the agent remember?[/bold]", guide_style="dim")
    checkpoint = tree.add(
        "Continue where [bold]this conversation[/bold] left off? "
        "-> [cyan]Checkpointer[/cyan] (config: thread_id)"
    )
    checkpoint.add("[dim]resume, retries, time travel, human-in-the-loop interrupts[/dim]")
    store = tree.add(
        "Recall facts in [bold]new conversations[/bold]? "
        "-> [magenta]Store[/magenta] (namespace: user_id, ...)"
    )
    store.add("[dim]preferences, profiles, knowledge shared across threads[/dim]")
    tree.add(
        "Shipping a production agent? -> [green]Both[/green]: compile(checkpointer=..., store=...)"
    )
    return Panel(tree, title="[bold]Which one do I need?[/bold]", border_style="yellow")


def render_tui(console: Console, results: dict[str, Any]) -> None:
    """Render the demos as framed panels: checkpoint | store, combined below."""

    panels = {key: build_panel(key, story) for key, story in results.items()}

    pair = [panels[key] for key in ("checkpoint", "store") if key in panels]
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

    if "combined" in panels:
        console.print(panels["combined"])

    console.print(build_decision_tree())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lg-memory-demo",
        description="Show LangGraph checkpoints vs stores with deterministic examples.",
    )
    parser.add_argument(
        "demo",
        choices=["checkpoint", "store", "both", "combined", "all"],
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
            "[bold]LangGraph persistence demo[/bold]\n"
            "Checkpoints save the graph's place; stores save durable memories.",
            title="checkpoints-vs-stores",
            border_style="cyan",
        )
    )
    render_tui(console, results)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
