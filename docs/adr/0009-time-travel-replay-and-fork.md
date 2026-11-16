# 0009. Time travel demo: replay and fork the same past checkpoint on one thread

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

Time travel is the fourth canonical checkpoint pattern the repo maps (see `README-USECASES-EXAMPLE.md`).

## Decision

`timetravel_demo` reuses the chapter 1 checkpoint graph on an in-memory saver:

1. It runs two turns.
2. It finds the snapshot whose `next == ("answer_from_thread",)` for the question "what is my name?".
3. **Replay:** it runs `invoke(None, snapshot.config)` and asserts the same reply.
4. **Fork:** it calls `update_state(snapshot.config, {"facts": ["name=Grace"]})` and then `invoke(None, forked_config)`. The `facts` add-reducer makes Grace the latest fact, so the fork answers Grace.
5. It asserts that the history grew (two timelines on one thread) and that the original reply is intact.

## Consequences

**Positive**
- Demonstrates that replay is a resume, not a cache read, and that forks are kept as an audit trail.

**Negative**
- The snapshot lookup depends on exact message text and node names. It raises `RuntimeError` if they drift.
- An in-memory saver means the demo does not show time travel across restarts.

## Alternatives considered

- None evidenced.

## Evidence

- `src/checkpoints_vs_stores/timetravel_demo.py`, `checkpoint_demo.py` (`facts` reducer)
- `tests/test_chapter3.py`
- Commit `e4d5ee6`
