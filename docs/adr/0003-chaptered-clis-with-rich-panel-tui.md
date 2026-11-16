# 0003. Chaptered CLIs sharing a `rich` panel TUI, with `--plain`, `--json` and `--no-color`

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The material grew in three steps: basics (checkpoint vs store), production backends, then human-in-the-loop and time travel.

## Decision

- One CLI module and console script per chapter: `lg-memory-demo` (`demo.py`), `lg-memory-demo2` (`chapter2.py`), `lg-memory-demo3` (`chapter3.py`). Each takes a demo name or `all`.
- Output is a `rich` dashboard by default: paired panels side by side when the console is at least `MIN_SIDE_BY_SIDE_WIDTH = 100` columns wide, stacked otherwise. Below that come a summary panel (decision tree, backend matrix table, or "Rules of the road").
- `--plain` prints flat text, `--json` prints `compact_json`, and `--no-color` disables ANSI colour. `rich` auto-detects TTYs, so `setup_and_run.sh` no longer passes `--no-color`.
- Later chapters import `MIN_SIDE_BY_SIDE_WIDTH` and `strip_heading` from `demo.py` rather than duplicating them.

## Consequences

**Positive**
- Each chapter is runnable on its own, and `make chapter2` / `make chapter3` mirror the CLIs.
- Layout behaviour is tested at 160 and 80 columns (`tests/test_combined_demo.py`).

**Negative**
- The three CLIs duplicate `render_tui`, `build_parser` and `main` with small variations, so changes must be made three times.
- Only chapter 1's TUI layout is tested. Chapter 2 and 3 TUIs are exercised only by `setup_and_run.sh` and the CI `chapter2 all --no-color` step.

## Alternatives considered

- A single CLI with subcommands per chapter: not taken (inferred from the separate `[project.scripts]` entries). The reason is not recorded (see A-001).

## Evidence

- `pyproject.toml` `[project.scripts]`
- `src/checkpoints_vs_stores/demo.py` (`MIN_SIDE_BY_SIDE_WIDTH`, `build_decision_tree`), `chapter2.py` (`build_matrix_panel`), `chapter3.py` (`RULES`)
- `tests/test_combined_demo.py`
- Commits `8d71b89` (TUI, decision tree, drop `--no-color` from setup script), `90cf816` (chapter 2), `e4d5ee6` (chapter 3)
