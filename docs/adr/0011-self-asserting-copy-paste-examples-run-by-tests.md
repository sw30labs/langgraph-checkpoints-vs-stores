# 0011. Minimal, self-asserting copy-paste examples, each executed by the test suite

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The demo modules carry scaffolding (ADR 0002), which makes them poor copy-paste material.

## Decision

`examples/01_checkpointer_minimal.py`, `02_store_minimal.py` and `03_both_minimal.py` are standalone scripts that depend only on `langgraph`. Each `assert`s the behaviour it claims. `tests/test_examples.py` globs `examples/*.py` and runs each one in a subprocess (60 s timeout), requiring exit code 0. `02_store_minimal.py` deliberately has no checkpointer, to isolate the store.

## Consequences

**Positive**
- Recipes can't silently rot. A new example is picked up by the glob automatically.

**Negative**
- Examples run with `sys.executable` from the repo root. They rely on `langgraph` being installed, not on the package.

## Alternatives considered

- Code snippets in the README only: replaced by runnable files (the README now links them).

## Evidence

- `examples/*.py`, `tests/test_examples.py`, `README.md` ("Use it in your own code")
- Commit `8d71b89`
