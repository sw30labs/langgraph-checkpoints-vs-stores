# 0008. Human-in-the-loop demo: durable `interrupt()` on SQLite, resumed by a rebuilt graph, counting node re-execution

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

Chapter 3 covers the two checkpoint patterns not yet shown: human-in-the-loop and time travel. The commit and module docstring single out one documented gotcha: on resume, the interrupted node re-executes from its start.

## Decision

- A three-node refund graph (`parse_request → approval_gate → execute_refund`) calls `interrupt()` in `approval_gate`.
- Runtime 1 invokes the graph until it pauses, with the paused state in a SQLite checkpointer. Runtime 2 opens a fresh saver and a fresh graph on the same file and resumes with `Command(resume={"approve": bool})`. Both approved and rejected paths run.
- A module-level counter `GATE_ENTRIES` records how many times the gate body runs. The test asserts `== 2`, proving re-execution. It lives at module level "because graph state written before an interrupt is not committed".
- `chapter3.RULES` distils five "docs-verified" rules, shown in a panel.

## Consequences

**Positive**
- Shows the idempotency hazard that tutorials usually skip.

**Negative**
- `GATE_ENTRIES` is keyed by `f"${amount}"`, not by thread, although the comment says "per thread". It works only because the two demo amounts differ (A-007).
- Runtime 2 is a new graph object in the same process, not a new process. It simulates a restart rather than proving one (contrast ADR 0006).
- The temp DB directory is not cleaned up (A-009).

## Alternatives considered

- Running HITL on `InMemorySaver`: rejected by the rule "use a durable checkpointer in production".

## Evidence

- `src/checkpoints_vs_stores/hitl_demo.py`, `chapter3.py` (`RULES`)
- `tests/test_chapter3.py`
- Commit `e4d5ee6`
