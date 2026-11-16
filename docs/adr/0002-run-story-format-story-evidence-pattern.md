# 0002. Demos return serializable evidence (`run_*_story`) separate from rendering (`format_*_story`)

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The same demo results feed several outputs: the terminal TUI, flat text (`--plain`), JSON (`--json`), committed artifacts, and pytest assertions.

## Decision

Each demo module exposes `run_<name>_story() -> dict` and `format_<name>_story(story) -> str`. The run function performs the real LangGraph calls and returns a JSON-friendly dict of evidence (replies, checkpoint counts, store items, a one-line `lesson`). The format function renders that dict as text. The CLIs (`demo.py`, `chapter2.py`, `chapter3.py`) `collect()` stories and choose a renderer. Tests assert on the dicts, not on rendered text.

## Consequences

**Positive**
- One source of truth for tests, artifacts, JSON and TUI.
- Tests read as specifications of the lesson (e.g. `thread_fresh_reply` must say "don't know").

**Negative**
- Demo modules carry scaffolding (result dicts, formatters). The README says so and points readers to `examples/` for minimal code (ADR 0011).

## Alternatives considered

- Print-only scripts: not evidenced. The pattern is consistent across all nine demo modules from the first commits.

## Evidence

- `src/checkpoints_vs_stores/{checkpoint,store,combined,resume,peek,search,matrix,hitl,timetravel}_demo.py`
- `src/checkpoints_vs_stores/demo.py`, `chapter2.py`, `chapter3.py` (`collect`, `render_text`, `render_tui`)
- `tests/test_*.py`
- `README.md` "Use it in your own code" ("The demo modules carry demo scaffolding")
- Commits `098ca92`, `698d703`
