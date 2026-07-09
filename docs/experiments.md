# Experiments

## Experiment 1: thread memory

Run:

```bash
python -m checkpoints_vs_stores.demo checkpoint
```

Expected result:

- `thread-alpha` remembers `Ada`.
- `thread-fresh` does not remember `Ada`.
- `graph.get_state_history(config)` shows multiple checkpoints for the thread.

## Experiment 2: cross-thread memory

Run:

```bash
python -m checkpoints_vs_stores.demo store
```

Expected result:

- `thread-a` stores `favorite_language=Python` for `user-ada`.
- `thread-b`, with the same `user_id`, recalls it.
- `thread-c`, with a different `user_id`, cannot recall it.

## Experiment 3: combined mental model

Run:

```bash
python -m checkpoints_vs_stores.demo both
```

Expected result:

- Checkpoint state stays thread-scoped.
- Store memory survives a thread switch.
