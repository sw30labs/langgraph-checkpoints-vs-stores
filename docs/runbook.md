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

## GitLab

Create a blank GitLab project, then push this repository:

```bash
git remote add origin git@gitlab.com:<namespace>/langgraph-checkpoints-vs-stores.git
git push -u origin main
```

The pipeline runs tests and regenerates demo artifacts.
