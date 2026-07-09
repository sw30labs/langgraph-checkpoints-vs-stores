"""Every recipe in examples/ must run standalone and exit 0."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = sorted((Path(__file__).resolve().parents[1] / "examples").glob("*.py"))


def test_examples_exist() -> None:
    assert EXAMPLES, "examples/ should contain at least one runnable recipe"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda path: path.name)
def test_example_runs_standalone(example: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(example)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
