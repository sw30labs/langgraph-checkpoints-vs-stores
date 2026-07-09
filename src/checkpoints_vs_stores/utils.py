"""Small deterministic parsing and formatting helpers for the demos."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def extract_after(text: str, marker: str) -> str | None:
    """Return title-cased text after a marker, if the marker exists.

    This intentionally avoids LLM calls so the examples are deterministic,
    free, and CI-friendly.
    """

    normalized = text.lower()
    marker_normalized = marker.lower()
    if marker_normalized not in normalized:
        return None
    start = normalized.index(marker_normalized) + len(marker_normalized)
    value = text[start:].strip(" .!?:;\n\t")
    return value.title() if value else None


def compact_json(data: Mapping[str, Any]) -> str:
    """Stable JSON for generated artifacts and snapshots."""

    return json.dumps(data, indent=2, sort_keys=True, default=str)
