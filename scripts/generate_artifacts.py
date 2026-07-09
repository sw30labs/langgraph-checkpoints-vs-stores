"""Generate demo outputs, comparison matrix, and SVG terminal artifact."""

from __future__ import annotations

import csv
import html
import json
import sys
from pathlib import Path
from copy import deepcopy
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from checkpoints_vs_stores.checkpoint_demo import (  # noqa: E402
    format_checkpoint_story,
    run_checkpoint_story,
)
from checkpoints_vs_stores.combined_demo import (  # noqa: E402
    format_combined_story,
    run_combined_story,
)
from checkpoints_vs_stores.store_demo import format_store_story, run_store_story  # noqa: E402
from checkpoints_vs_stores.utils import compact_json  # noqa: E402

ARTIFACTS = ROOT / "artifacts"
SAMPLE_OUTPUT = ARTIFACTS / "sample-output"
ASSETS = ROOT / "docs" / "assets"




def normalize_volatile_values(data: Any) -> Any:
    """Redact timestamps and generated checkpoint ids for stable committed artifacts."""

    if isinstance(data, dict):
        normalized: dict[str, Any] = {}
        for key, value in data.items():
            if key == "latest_checkpoint_id":
                normalized[key] = "<checkpoint-id>"
            elif key in {"created_at", "updated_at"}:
                normalized[key] = "<timestamp>"
            else:
                normalized[key] = normalize_volatile_values(value)
        return normalized
    if isinstance(data, list):
        return [normalize_volatile_values(item) for item in data]
    return data


COMPARISON_ROWS = [
    {
        "dimension": "main_purpose",
        "checkpoint": "Save graph state snapshots so a thread can resume or be inspected.",
        "store": "Save application-defined key-value data for durable memory.",
    },
    {
        "dimension": "scope",
        "checkpoint": "Single thread_id lineage.",
        "store": "Namespace can be shared across threads, users, tenants, or apps.",
    },
    {
        "dimension": "owned_by",
        "checkpoint": "LangGraph runtime writes checkpoints when configured.",
        "store": "Application nodes decide what to put/get/search/delete.",
    },
    {
        "dimension": "demo_proof",
        "checkpoint": "thread-alpha remembers Ada; thread-fresh does not.",
        "store": "thread-b recalls Python for user-ada; user-grace does not.",
    },
    {
        "dimension": "production_backend",
        "checkpoint": "Use persistent checkpointer, e.g. Postgres or SQLite.",
        "store": "Use persistent store, e.g. Postgres, MongoDB, or Redis.",
    },
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_comparison_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["dimension", "checkpoint", "store"])
        writer.writeheader()
        writer.writerows(COMPARISON_ROWS)


def terminal_svg(lines: list[str]) -> str:
    visible_lines = lines[:24]
    height = 96 + len(visible_lines) * 22
    escaped_lines = [html.escape(line) for line in visible_lines]
    text_nodes = "\n".join(
        f'<text x="42" y="{92 + index * 22}" class="line">{line}</text>'
        for index, line in enumerate(escaped_lines)
    )
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-label="Demo terminal output">
  <defs>
    <linearGradient id="termBg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <style>
      .chrome{{fill:#0f172a;stroke:#334155;stroke-width:1.2}}
      .dot1{{fill:#ef4444}} .dot2{{fill:#f59e0b}} .dot3{{fill:#22c55e}}
      .title{{font-family:Inter,Arial,sans-serif;font-size:15px;font-weight:700;fill:#cbd5e1}}
      .line{{font-family:'JetBrains Mono','Fira Code',monospace;font-size:14px;fill:#d1fae5}}
    </style>
  </defs>
  <rect width="1100" height="{height}" fill="url(#termBg)" rx="24"/>
  <rect x="22" y="22" width="1056" height="44" class="chrome" rx="16"/>
  <circle cx="52" cy="44" r="7" class="dot1"/>
  <circle cx="76" cy="44" r="7" class="dot2"/>
  <circle cx="100" cy="44" r="7" class="dot3"/>
  <text x="132" y="49" class="title">python -m checkpoints_vs_stores.demo all --no-color</text>
  {text_nodes}
</svg>
""".strip()


def main() -> int:
    checkpoint = normalize_volatile_values(deepcopy(run_checkpoint_story()))
    store = normalize_volatile_values(deepcopy(run_store_story()))
    combined = normalize_volatile_values(deepcopy(run_combined_story()))

    write_text(SAMPLE_OUTPUT / "checkpoint_demo.txt", format_checkpoint_story(checkpoint))
    write_text(SAMPLE_OUTPUT / "store_demo.txt", format_store_story(store))
    write_text(SAMPLE_OUTPUT / "combined_demo.txt", format_combined_story(combined))

    summary: dict[str, Any] = {
        "checkpoint": checkpoint,
        "store": store,
        "combined": combined,
    }
    write_text(ARTIFACTS / "demo-summary.json", compact_json(summary))
    write_comparison_csv(ARTIFACTS / "comparison-matrix.csv")

    all_output = "\n\n".join(
        [
            format_checkpoint_story(checkpoint),
            format_store_story(store),
            format_combined_story(combined),
        ]
    )
    write_text(ASSETS / "terminal-demo.svg", terminal_svg(all_output.splitlines()))

    print(json.dumps({"generated": str(ARTIFACTS), "assets": str(ASSETS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
