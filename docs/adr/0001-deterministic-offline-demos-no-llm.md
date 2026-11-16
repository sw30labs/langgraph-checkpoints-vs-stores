# 0001. Deterministic, offline demos with no LLM calls or API keys

- **Status:** Accepted, retrospective, inferred 2026-11-16
- **Deciders:** Nic Cravino (repository author)

## Context

The repo exists to show the difference between LangGraph checkpoints (thread-scoped graph state) and stores (cross-thread memory). An LLM in the loop would make outputs vary between runs, cost money, and need credentials in CI.

## Decision

Every demo uses real LangGraph `StateGraph` graphs, but each node is plain Python. Text parsing (`extract_after`) is deterministic string matching, and the semantic-search demo uses a toy hashed-trigram embedding instead of a model. Nothing needs an API key or network access, apart from the optional Postgres/Redis backends.

The stated reason is in code: `extract_after` "intentionally avoids LLM calls so the examples are deterministic, free, and CI-friendly".

## Consequences

**Positive**
- Outputs are reproducible, so tests can assert exact strings and committed artifacts stay byte-stable (ADR 0010).
- Runs in CI and offline with zero secrets. The README advertises "LLM calls: none, runs offline".

**Negative**
- The "agent" behaviour is toy keyword matching. Readers must carry the pattern over to real LLM nodes themselves.
- Behaviours that only show up with an LLM (re-executed LLM calls on replay or resume) are described in text rather than demonstrated with a real model.

## Alternatives considered

- Real LLM calls behind an API key: not taken (evidence: README "No LLM calls and no API keys"). A mocked LLM client was not evidenced either way.

## Evidence

- `src/checkpoints_vs_stores/utils.py` (`extract_after` docstring)
- `src/checkpoints_vs_stores/checkpoint_demo.py` module docstring ("does not use an LLM, which keeps the demo deterministic and runnable in CI")
- `src/checkpoints_vs_stores/search_demo.py` module docstring
- `README.md` (badge "LLM calls: none, runs offline"; "No LLM calls and no API keys")
- Commits `098ca92` (checkpoint demo + utils), `35ad18e` (offline badge)
