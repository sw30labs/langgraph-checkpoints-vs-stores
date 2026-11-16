# 0014. src-layout setuptools package, Python ≥ 3.10, and a one-shot bootstrap script that installs non-editable

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

Readers should get from clone to green in one command on macOS, where the system `python3` can be 3.9 and repos may live in iCloud-synced folders.

## Decision

- The package lives in `src/checkpoints_vs_stores/` (setuptools `packages.find where = ["src"]`), with `requires-python = ">=3.10"` and `langgraph>=1.2.8,<2.0.0`.
- `tests/conftest.py` and `scripts/generate_artifacts.py` insert `src/` onto `sys.path`, so they run from a raw checkout.
- `setup_and_run.sh` probes `python3.13` down to `python3` for one that is at least 3.10, then:
  1. creates `.venv`;
  2. installs `.[dev]` **non-editable**;
  3. runs ruff, pytest, and all three chapters.
- The stated reason for non-editable: "editable (.pth-based) installs are silently skipped by Python 3.13 when the file gets a macOS hidden flag (e.g. in iCloud-synced dirs)".
- The Makefile and `docs/runbook.md` keep `pip install -e ".[dev]"` for the manual path.

## Consequences

**Positive**
- `./setup_and_run.sh` is a single verification command.

**Negative**
- Two install paths (editable in Makefile/runbook/CI, non-editable in the script) behave differently for local edits (A-010).

## Alternatives considered

- Editable install everywhere: rejected for the script, for the macOS reason above.

## Evidence

- `pyproject.toml`, `setup_and_run.sh`, `Makefile`, `docs/runbook.md`, `tests/conftest.py`, `scripts/generate_artifacts.py`, `.gitignore` (AppleDouble `._*` and iCloud notes)
- Commits `433f566`, `2707a62`
