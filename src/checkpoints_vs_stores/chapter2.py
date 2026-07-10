"""Chapter 2 CLI: production persistence backends.

Mirrors the Chapter 1 CLI (`checkpoints_vs_stores.demo`) but for the
production story: kill-and-resume on SQLite, a peek at raw database rows,
offline semantic search, and the same graph running on four backends.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from checkpoints_vs_stores.demo import MIN_SIDE_BY_SIDE_WIDTH, strip_heading
from checkpoints_vs_stores.matrix_demo import format_matrix_story, run_matrix_story
from checkpoints_vs_stores.peek_demo import format_peek_story, run_peek_story
from checkpoints_vs_stores.resume_demo import format_resume_story, run_resume_story
from checkpoints_vs_stores.search_demo import format_search_story, run_search_story
from checkpoints_vs_stores.utils import compact_json

SECTIONS = {
    "resume": ("Kill-and-resume - SQLite", "cyan", format_resume_story),
    "peek": ("Inside the database", "magenta", format_peek_story),
    "search": ("Semantic search - store index", "green", format_search_story),
}


def collect(command: str) -> dict[str, Any]:
    """Run one or more chapter 2 demos and return a dictionary of results."""

    if command == "resume":
        return {"resume": run_resume_story()}
    if command == "peek":
        return {"peek": run_peek_story()}
    if command == "search":
        return {"search": run_search_story()}
    if command == "matrix":
        return {"matrix": run_matrix_story()}
    if command == "all":
        return {
            "resume": run_resume_story(),
            "peek": run_peek_story(),
            "search": run_search_story(),
            "matrix": run_matrix_story(),
        }
    raise ValueError(f"Unsupported chapter 2 command: {command}")


def render_text(results: dict[str, Any]) -> str:
    """Render collected results as plain text."""

    formatters = {key: formatter for key, (_, _, formatter) in SECTIONS.items()}
    formatters["matrix"] = format_matrix_story
    sections = [formatters[key](story) for key, story in results.items()]
    return "\n\n" + "\n\n".join(sections)


def build_panel(key: str, story: dict[str, Any]) -> Panel:
    """Wrap one demo's formatted output in a titled, colored frame."""

    title, border, formatter = SECTIONS[key]
    body = Text(strip_heading(formatter(story)))
    body.highlight_regex(r"(?m)^Lesson: .+$", "bold")
    return Panel(body, title=f"[bold]{title}[/bold]", border_style=border, padding=(1, 2))


def build_matrix_panel(story: dict[str, Any]) -> Panel:
    """Render the backend matrix as a table, like a tiny ops dashboard."""

    table = Table(box=None, expand=True, pad_edge=False)
    table.add_column("backend", style="bold")
    table.add_column("status")
    table.add_column("recommended for")
    table.add_column("proof / hint")
    styles = {"ok": "green", "unreachable": "yellow", "error": "red", "failed": "red"}
    for row in story["rows"]:
        proof = row.get("recall_reply") or row.get("detail", "")
        table.add_row(
            row["backend"],
            f"[{styles.get(row['status'], 'white')}]{row['status']}[/]",
            row["recommended_for"],
            proof,
        )
    footer = Text(f"\n{story['lesson']}", style="bold")
    return Panel(
        Group(table, footer),
        title="[bold]Backend matrix - one graph, four backends[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


def render_tui(console: Console, results: dict[str, Any]) -> None:
    """Framed panels: resume | peek side by side, search below, matrix last."""

    pair = [build_panel(key, results[key]) for key in ("resume", "peek") if key in results]
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

    if "search" in results:
        console.print(build_panel("search", results["search"]))
    if "matrix" in results:
        console.print(build_matrix_panel(results["matrix"]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lg-memory-demo2",
        description="Chapter 2: LangGraph persistence on production backends.",
    )
    parser.add_argument(
        "demo",
        choices=["resume", "peek", "search", "matrix", "all"],
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
            "[bold]Chapter 2: production backends[/bold]\n"
            "Same graphs as chapter 1 - now the memory survives the process.",
            title="checkpoints-vs-stores",
            border_style="cyan",
        )
    )
    render_tui(console, results)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
