"""Generate demo outputs, comparison matrix, and demo summary JSON."""

from __future__ import annotations

import csv
import json
import sys
from copy import deepcopy
from pathlib import Path
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

    print(json.dumps({"generated": str(ARTIFACTS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
