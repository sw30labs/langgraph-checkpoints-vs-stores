.PHONY: install test demo checkpoint store both chapter2 backends-up backends-down artifacts clean

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

chapter2:
	python -m checkpoints_vs_stores.chapter2 all

backends-up:
	docker compose up -d --wait

backends-down:
	docker compose down -v

artifacts:
	python scripts/generate_artifacts.py

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage build dist
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
