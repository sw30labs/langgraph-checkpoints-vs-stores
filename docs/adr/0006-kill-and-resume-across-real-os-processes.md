# 0006. Prove durable resume with two real OS processes on one SQLite file

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

A durable checkpointer's key claim is that a thread survives the process that created it. Running both turns in a single process would not prove it.

## Decision

`resume_demo` runs each conversation phase in a separate `subprocess.run([sys.executable, "-m", "checkpoints_vs_stores.resume_demo", "--phase", N, "--db", path])` against the same SQLite file.

- `PYTHONPATH` is prefixed with the `src` dir.
- Each run has a 120 s timeout and `check=True`.
- Each phase prints JSON including its PID.
- The test asserts that the two PIDs differ from each other and from the orchestrator, and that phase 2 recalls "Ada".

## Consequences

**Positive**
- The persistence claim is demonstrated, not just described: "InMemorySaver could never do this".

**Negative**
- Slower than in-process tests, and depends on the interpreter's ability to re-import the package (hence the `PYTHONPATH` injection).
- The temp directories from `tempfile.mkdtemp` are never removed (A-009).

## Alternatives considered

- Rebuilding the saver in-process: this weaker form is used instead in `hitl_demo` (ADR 0008). For crash recovery the author chose real processes. The reason is inferred from the module docstring.

## Evidence

- `src/checkpoints_vs_stores/resume_demo.py`
- `tests/test_chapter2.py::test_resume_survives_process_death`
- Commit `90cf816`
