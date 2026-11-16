# 0004. A backend factory: one graph, four persistence backends

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

Chapter 2 shows that moving from the in-memory checkpointer and store to production backends needs no change to graph code.

## Decision

`backends.py` provides `open_checkpointer(backend)` and `open_store(backend, index=None)` context managers for `memory`, `sqlite`, `postgres` and `redis`.

- Imports are lazy, one per branch, so the Postgres and Redis libraries are only needed when used.
- Persistent backends call `.setup()` before yielding.
- `server_reachable()` is a cheap TCP probe. It treats `memory` and `sqlite` as always reachable.
- `build_checkpoint_graph(checkpointer=None)` accepts any checkpointer, so the chapter 1 graph is reused unchanged.

Packaging follows the same split. `langgraph-checkpoint-sqlite` is a core dependency. The Postgres and Redis savers and `psycopg[binary]` live in the optional `backends` extra, which `dev` includes.

## Consequences

**Positive**
- `matrix_demo` proves that the same write-in-thread-A / recall-in-thread-B round trip works on every backend.
- A base install stays light. The README states that only `memory` and `sqlite` work out of the box.

**Negative**
- MongoDB appears in `docs/production-notes.md`, `README-USECASES-EXAMPLE.md` and the comparison CSV as a production store, but the factory does not implement it (A-006).
- Unknown backend names raise `ValueError` at runtime rather than being rejected by the type system.

## Alternatives considered

- Per-backend copies of each demo graph: rejected in spirit by the docstring ("swapping backends never touches graph code — only this factory").

## Evidence

- `src/checkpoints_vs_stores/backends.py`, `matrix_demo.py`, `checkpoint_demo.py` (`build_checkpoint_graph`)
- `pyproject.toml` (`dependencies`, `[project.optional-dependencies] backends`, `dev`)
- Commit `90cf816` ("backends extra in pyproject (sqlite saver moves to core deps)")
