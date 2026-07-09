# Concepts: checkpoint vs store

LangGraph has two complementary persistence tools:

| Concept | Mental model | Scope | Stores what? | Great for |
|---|---|---:|---|---|
| Checkpoint | Session autosave | One thread | Graph state snapshots | Resume, conversation continuity, interrupts, time travel, fault tolerance |
| Store | Durable memory database | Cross-thread | App-defined key-value data | User preferences, facts, profile memory, shared knowledge |

## Checkpoint

A checkpoint is a saved snapshot of graph state. In this repo, the checkpoint demo stores a user's name in the thread state. The same `thread_id` can recall it. A different `thread_id` cannot.

## Store

A store is a namespace/key/value memory layer. In this repo, the store demo writes `favorite_language=Python` under a user namespace. A different thread with the same `user_id` can recall it. A different `user_id` cannot.

## Rule of thumb

Use checkpoints when the graph needs to remember where **this thread** is. Use stores when the application needs to remember something about **this user/app** beyond the thread.
