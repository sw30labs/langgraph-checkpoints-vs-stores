# Ultraplan

This repo is designed as a small, reviewable museum exhibit for LangGraph persistence.

## Mission

Make the distinction between **checkpoints** and **stores** obvious by showing behavior, not just definitions.

## What this project proves

1. A checkpoint keeps a graph thread's state alive across invocations with the same `thread_id`.
2. A fresh `thread_id` gets a fresh checkpoint lineage.
3. A store keeps application memory outside graph state.
4. A store can be read from another thread when the namespace, such as `user_id`, is the same.
5. Most real agents use both: checkpoints for the current run and stores for durable memories.

## Review path

1. Read the README hero section.
2. Inspect `src/checkpoints_vs_stores/checkpoint_demo.py`.
3. Inspect `src/checkpoints_vs_stores/store_demo.py`.
4. Run `python -m checkpoints_vs_stores.demo all`.
5. Run `pytest`.
6. Open the SVG diagrams in `docs/assets`.
7. Push to GitLab and let `.gitlab-ci.yml` run.
