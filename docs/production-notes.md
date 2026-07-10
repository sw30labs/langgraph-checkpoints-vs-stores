# Production notes

Chapter 1 intentionally uses `InMemorySaver` and `InMemoryStore` so the examples run locally without databases or API keys. Chapter 2 (`python -m checkpoints_vs_stores.chapter2 all`) demonstrates the production swaps end to end: SQLite kill-and-resume, raw database rows, semantic search, and the same graph on Postgres and Redis via `docker compose up -d`.

For real deployments:

- Replace in-memory checkpointing with a persistent checkpointer such as Postgres or SQLite.
- Replace in-memory store with a persistent store such as Postgres, MongoDB, or Redis.
- Keep `thread_id` values short, stable, and unique.
- Namespace store data intentionally, for example `(tenant_id, user_id, "memories")`.
- Add retention rules for checkpoint history if conversations can be long.
- Avoid storing secrets or raw private data unless the storage backend and retention policy are designed for that.

## Decision guide

| Situation | Use checkpoint | Use store |
|---|:---:|:---:|
| Resume an interrupted graph run | ✅ | ❌ |
| Recall the previous message in the same chat | ✅ | Usually no |
| Remember a preference next week in a new chat | ❌ | ✅ |
| Inspect history for debugging/time travel | ✅ | ❌ |
| Share a fact across subgraphs/threads | Sometimes | ✅ |
| Persist arbitrary app metadata | ❌ | ✅ |
