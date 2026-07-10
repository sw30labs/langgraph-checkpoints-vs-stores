#!/usr/bin/env bash
# One-shot setup + verification: creates .venv, installs the package,
# runs lint + tests, then runs all three demos.
set -euo pipefail

cd "$(dirname "$0")"

# The project needs Python >= 3.10; plain `python3` may be older (macOS ships 3.9).
find_python() {
  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 &&
       "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

PYTHON="$(find_python)" || {
  echo "error: no Python >= 3.10 found on PATH" >&2
  exit 1
}
echo "==> Using $PYTHON ($("$PYTHON" --version))"

if [ ! -x .venv/bin/python ]; then
  echo "==> Creating .venv"
  "$PYTHON" -m venv .venv
fi

echo "==> Installing package + dev tools"
.venv/bin/python -m pip install --quiet --upgrade pip
# Non-editable install: editable (.pth-based) installs are silently skipped by
# Python 3.13 when the file gets a macOS hidden flag (e.g. in iCloud-synced dirs).
.venv/bin/python -m pip install --quiet ".[dev]"

echo "==> Lint (ruff)"
.venv/bin/ruff check src tests scripts examples
.venv/bin/ruff format --check src tests scripts examples

echo "==> Tests (pytest)"
.venv/bin/python -m pytest

echo "==> Demos"
# Rich auto-detects the terminal: colored TUI panels on a TTY, plain when piped.
.venv/bin/python -m checkpoints_vs_stores.demo all

echo "==> Chapter 2 (postgres/redis rows need: docker compose up -d)"
.venv/bin/python -m checkpoints_vs_stores.chapter2 all

echo "==> Chapter 3"
.venv/bin/python -m checkpoints_vs_stores.chapter3 all

echo "==> All good: lint clean, tests green, demos ran."
