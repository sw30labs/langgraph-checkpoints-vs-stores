# 0005. Optional Postgres and Redis through Docker Compose on non-standard ports, degrading to a hint when absent

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The Postgres and Redis demos need live servers, but most readers will run the repo without them, and some will already have local servers on the default ports.

## Decision

- `docker-compose.yml` runs `pgvector/pgvector:pg16` on host port **5442** and `redis:8` on host port **6390**, both with healthchecks. The stated reasons: non-standard ports "so nothing clashes with locally installed servers", and Redis 8 "bundles the JSON and search modules the LangGraph integration needs".
- Connection URLs default to those ports and can be overridden with `LG_DEMO_POSTGRES_URL` and `LG_DEMO_REDIS_URL`.
- When a server is unreachable, the matrix reports `unreachable` with the fix command rather than failing. Postgres and Redis tests `skipif` the server is down.
- CI runs the same images as service containers on the same ports in a `backend-integration` job, so those tests do run in CI.
- `make backends-up` / `make backends-down` wrap `docker compose up -d --wait` and `down -v`.

## Consequences

**Positive**
- `pytest` and `chapter2 all` stay green on a laptop with no Docker.
- Real backend coverage still happens in CI.

**Negative**
- Locally, a skipped test can hide a backend regression. Only CI catches it.
- The demo password `postgres` is hard-coded in the compose file, CI and the default URL. This is fine for a local demo but must not be copied to production. It is a demo credential, not a secret.

## Alternatives considered

- Default ports 5432 and 6379: rejected (comment in `docker-compose.yml` and `backends.py`).
- Making the backends mandatory for tests: not taken (`skipif` markers).

## Evidence

- `docker-compose.yml`, `src/checkpoints_vs_stores/backends.py`, `matrix_demo.py`, `tests/test_chapter2.py`, `.github/workflows/ci.yml` (`backend-integration`), `Makefile`, `README.md` (Chapter 2)
- Commit `90cf816`
