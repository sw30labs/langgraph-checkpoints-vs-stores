# 0013. License: Apache 2.0 (switched from MIT)

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

The initial commit shipped a 21-line `LICENSE` (MIT, per the later commit message).

## Decision

Commit `35ad18e` switched to Apache 2.0 across `LICENSE` (canonical text), `pyproject.toml` (`license = {text = "Apache-2.0"}`) and the README badge and footer. The three are consistent at `e4d5ee6`.

## Consequences

**Positive**
- Explicit patent grant and contribution terms. LICENSE, pyproject and README agree, unlike some sibling repos where they diverged.

**Negative**
- None evidenced.

## Alternatives considered

- MIT: the original license, replaced. The reason is not recorded (A-003).

## Evidence

- `LICENSE`, `pyproject.toml`, `README.md`
- Commits `29720a8`, `35ad18e` ("License changes from MIT to Apache 2.0")
