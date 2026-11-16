# 0007. Offline semantic search with a toy hashed-trigram embedding

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

Store semantic search (`index={"embed": ..., "dims": ...}` plus `store.search(query=...)`) normally needs an embedding model. That conflicts with ADR 0001 (offline, no keys).

## Decision

`search_demo.trigram_embed` builds a 64-dimensional, L2-normalised vector from MD5-hashed lowercase character trigrams. It is passed as the store `index` on the SQLite store, so the Store API calls are the ones a production model would use. Three memories are stored, two queries are run, and each query's expected top key is asserted in tests. The output carries an explicit disclaimer: "Toy trigram embeddings keep this offline; use a real model in production."

## Consequences

**Positive**
- Shows the real index-config and search API with deterministic ranking and no network.

**Negative**
- The ranking is lexical, not semantic. It works only because the queries share trigrams with the target memories, and it could mislead a reader who skips the disclaimer.
- MD5 is used for hashing only, not security, so this is not a security concern.

## Alternatives considered

- A real embedding model (OpenAI or local): named in the module docstring as the production swap, but not used.

## Evidence

- `src/checkpoints_vs_stores/search_demo.py`, `backends.py` (`open_store(..., index=...)`)
- `tests/test_chapter2.py::test_search_ranks_memories_by_meaning`
- Commit `90cf816`
