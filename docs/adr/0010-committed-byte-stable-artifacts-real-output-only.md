# 0010. Committed, byte-stable artifacts; the README quotes only real captured output

- **Status:** Accepted, retrospective, inferred 2026-11-16

## Context

An early version of the README used a terminal screenshot SVG and poster SVGs. The commit that removed them calls the screenshot "fabricated".

## Decision

- `scripts/generate_artifacts.py` (`make artifacts`) reruns the three chapter 1 demos. It writes `artifacts/sample-output/*.txt`, `artifacts/demo-summary.json` and `artifacts/comparison-matrix.csv`.
- `normalize_volatile_values` redacts `latest_checkpoint_id`, `created_at` and `updated_at`, so the files are byte-stable across reruns.
- The README quotes these files verbatim. Hand-drawn SVGs and the terminal-SVG generator were deleted, and diagrams became inline Mermaid plus `diagrams/*.mmd` sources.
- CI's `demo-artifacts` job regenerates and uploads `artifacts/` (14-day retention).

## Consequences

**Positive**
- Documentation cannot claim output that the code doesn't produce, as long as artifacts are regenerated.

**Negative**
- CI regenerates artifacts but does not fail on a diff against the committed copies, so drift is possible (A-008).
- Only chapter 1 is covered. Chapter 2 and 3 output is described in prose, not captured.

## Alternatives considered

- Illustrative SVGs and screenshots: tried, then removed (`02d43fb`, `08382a2`).

## Evidence

- `scripts/generate_artifacts.py`, `artifacts/`, `diagrams/`, `README.md` ("Every output quoted below is captured from a real run")
- `.github/workflows/ci.yml` (`demo-artifacts`)
- Commits `a552532`, `1a7e6de` ("stabilize generated artifacts"), `02d43fb`, `08382a2` ("Replace the fabricated terminal screenshot and poster SVGs with output captured from real runs")
