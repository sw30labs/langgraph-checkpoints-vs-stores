# 0015. A separate, source-verified use-case guide, with inferences and vendor numbers labelled

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The main README shows *how* checkpoints and stores behave. Readers also ask *when* to use them.

## Decision

`README-USECASES-EXAMPLE.md` maps four checkpoint patterns and four store patterns to production case studies and backends. The main README links to it from a top-of-page tip and the decision-tree section. Its stated method: "Every claim below was checked against live primary sources on 2026-07-09 … where a claim is an inference rather than a documented fact, it is labeled as such." For example, Replit's checkpointer use is marked as an inference, and enterprise numbers as vendor-reported. A closing table maps each use case to the runnable demo that proves it.

## Consequences

**Positive**
- Keeps marketing-style claims out of the code README and makes sourcing explicit.

**Negative**
- External facts age. The guide is dated 2026-07-09 and has no refresh process.
- Its backend table lists no SQLite store ("—"), while this repo's `backends.py` and `peek_demo.py` use `langgraph.store.sqlite.SqliteStore` (A-005).

## Alternatives considered

- Folding the material into the main README: not taken. The reason is not recorded.

## Evidence

- `README-USECASES-EXAMPLE.md`, `README.md` (tip callout)
- Commits `055525d`, `9446d94`, `90cf816`, `e4d5ee6` (guide mapping updated)
