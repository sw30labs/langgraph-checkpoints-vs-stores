# Architecture Decision Records

Written retrospectively on 2026-11-16 from a full read of `main` at `e4d5ee6` (source, tests, config, docs, artifacts and the full git history). Format: Title; Status; Context; Decision; Consequences (positive/negative); Alternatives considered; Evidence. ADR 0016 was added 2026-11-23 as a forward-looking proposal, not a retrospective record. Where a rationale is inferred rather than stated, it is labelled and logged in [`../assumptions.md`](../assumptions.md).

| # | Decision | Status |
|---|---|---|
| [0001](0001-deterministic-offline-demos-no-llm.md) | Deterministic, offline demos with no LLM calls or API keys | Accepted (retrospective) |
| [0002](0002-run-story-format-story-evidence-pattern.md) | Demos return serializable evidence (`run_*_story`) separate from rendering (`format_*_story`) | Accepted (retrospective) |
| [0003](0003-chaptered-clis-with-rich-panel-tui.md) | Chaptered CLIs sharing a `rich` panel TUI, with `--plain`, `--json` and `--no-color` | Accepted (retrospective) |
| [0004](0004-backend-factory-one-graph-four-backends.md) | A backend factory: one graph, four persistence backends | Accepted (retrospective) |
| [0005](0005-docker-compose-backends-nonstandard-ports-degrade-gracefully.md) | Optional Postgres and Redis through Docker Compose on non-standard ports, degrading gracefully | Accepted (retrospective) |
| [0006](0006-kill-and-resume-across-real-os-processes.md) | Prove durable resume with two real OS processes on one SQLite file | Accepted (retrospective) |
| [0007](0007-offline-semantic-search-with-toy-trigram-embeddings.md) | Offline semantic search with a toy hashed-trigram embedding | Accepted (retrospective) |
| [0008](0008-hitl-interrupt-durable-pause-and-reexecution-proof.md) | Human-in-the-loop: durable `interrupt()`, rebuilt-graph resume, node re-execution proof | Accepted (retrospective) |
| [0009](0009-time-travel-replay-and-fork.md) | Time travel: replay and fork the same past checkpoint | Accepted (retrospective) |
| [0010](0010-committed-byte-stable-artifacts-real-output-only.md) | Committed, byte-stable artifacts; the README quotes only real captured output | Accepted (retrospective) |
| [0011](0011-self-asserting-copy-paste-examples-run-by-tests.md) | Minimal self-asserting examples executed by the test suite | Accepted (retrospective) |
| [0012](0012-github-actions-ci-replacing-gitlab.md) | GitHub Actions CI replacing GitLab CI | Accepted (retrospective) |
| [0013](0013-apache-2-0-license.md) | License: Apache 2.0 (switched from MIT) | Accepted (retrospective) |
| [0014](0014-src-layout-setuptools-nonedit-bootstrap.md) | src-layout package, Python ≥ 3.10, non-editable bootstrap script | Accepted (retrospective) |
| [0015](0015-source-verified-use-case-guide.md) | A separate, source-verified use-case guide | Accepted (retrospective) |
| [0016](0016-langmem-retrieval-patterns.md) | LangMem retrieval patterns for enterprise LangGraph: prompt-function injection primary, gated background consolidation secondary (forward-looking, not evidenced by this repo) | Proposed (2026-11-23) |

To add a decision, copy the format above, take the next number, and add a row here.
