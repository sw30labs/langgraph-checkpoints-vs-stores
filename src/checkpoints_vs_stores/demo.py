"""Command-line interface for the LangGraph persistence demos."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import Any

from rich.console import Console
from rich.panel import Panel

from checkpoints_vs_stores.checkpoint_demo import (
    format_checkpoint_story,
    run_checkpoint_story,
)
from checkpoints_vs_stores.combined_demo import format_combined_story, run_combined_story
from checkpoints_vs_stores.store_demo import format_store_story, run_store_story
from checkpoints_vs_stores.utils import compact_json


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
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = collect(args.demo)

    if args.json:
        print(compact_json(results))
        return 0

    console = Console(color_system=None if args.no_color else "auto")
    console.print(
        Panel.fit(
            "[bold]LangGraph persistence demo[/bold]\n"
            "Checkpoints save the graph's place; stores save durable memories.",
            title="checkpoints-vs-stores",
            border_style="cyan" if not args.no_color else None,
        )
    )
    console.print(render_text(results))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
