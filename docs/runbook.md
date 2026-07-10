# Runbook

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run all demos

```bash
python -m checkpoints_vs_stores.demo all
```

## Generate artifacts

```bash
python scripts/generate_artifacts.py
```

## Test

```bash
pytest
```

## CI

The repository lives at
<https://github.com/sw30labs/langgraph-checkpoints-vs-stores>. GitHub Actions
([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) lints, tests on
Python 3.10 and 3.13, and regenerates demo artifacts on every push and pull
request.
