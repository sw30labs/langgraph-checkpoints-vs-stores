.PHONY: install test demo checkpoint store both artifacts clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

demo:
	python -m checkpoints_vs_stores.demo all

checkpoint:
	python -m checkpoints_vs_stores.demo checkpoint

store:
	python -m checkpoints_vs_stores.demo store

both:
	python -m checkpoints_vs_stores.demo both

artifacts:
	python scripts/generate_artifacts.py

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
