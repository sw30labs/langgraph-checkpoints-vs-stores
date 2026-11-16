# 0012. GitHub Actions CI (replacing GitLab CI): lint, a 3.10/3.13 test matrix, backend integration, artifacts

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The repo was initialised "GitLab-ready" (`29720a8`), with `.gitlab-ci.yml` and GitLab issue and MR templates (`aef5f54`). It was then prepared for public release on GitHub under `sw30labs`.

## Decision

`.gitlab-ci.yml` and the `.gitlab/` templates were removed. `.github/workflows/ci.yml` runs on pushes to `main` and on every PR:

- `lint`: `ruff check` and `ruff format --check` over `src tests scripts examples` on Python 3.13.
- `tests`: `pytest` on Python 3.10 and 3.13.
- `backend-integration`: Postgres and Redis service containers.
- `demo-artifacts`: needs lint and tests.

Actions were bumped to Node 24 majors (`checkout@v7`, `setup-python@v6`, `upload-artifact@v7`). Ruff is configured with line length 100, target `py310`, rules `E,F,I,UP,B`.

## Consequences

**Positive**
- Tests cover both ends of the supported Python range (`requires-python >= 3.10`).
- Every push to `main` from `aa1da63` to `e4d5ee6` concluded `success` (via `gh run list`, 2026-11-16).

**Negative**
- Docs (`docs/`, READMEs) are not linted or link-checked.

## Alternatives considered

- Keeping GitLab CI: replaced. The reason for the move is inferred from the GitHub remote and the README badges (A-002).

## Evidence

- `.github/workflows/ci.yml`, `pyproject.toml` (`[tool.ruff]`), `docs/runbook.md` (CI section)
- Commits `29720a8`, `aef5f54`, `02d43fb`, `aa1da63` ("replace GitLab CI with GitHub Actions"), `18d2726` (Node 24 majors), `90cf816` (backend-integration job)
