"""Combined demo that shows checkpoint state and store memory side by side."""

from __future__ import annotations

from typing import Any

from checkpoints_vs_stores.store_demo import UserContext, build_store_graph, serialize_store_items


def run_combined_story() -> dict[str, Any]:
    """Run a scenario that uses both persistence layers at once."""

    graph, store = build_store_graph()
    ada = UserContext(user_id="user-ada")

    thread_a = {"configurable": {"thread_id": "thread-a"}}
    thread_b = {"configurable": {"thread_id": "thread-b"}}

    graph.invoke({"user_message": "my favorite language is Python"}, thread_a, context=ada)
    thread_b_result = graph.invoke(
        {"user_message": "what language do I like?"}, thread_b, context=ada
    )

    thread_a_state = graph.get_state(thread_a)
    thread_b_state = graph.get_state(thread_b)
    store_items = serialize_store_items(store.search(("user-ada", "profile"), limit=10))

    return {
        "lesson": "Use both: checkpoint for per-thread state, store for durable memory.",
        "thread_b_reply": thread_b_result["reply"],
        "thread_a_checkpoint_values": thread_a_state.values,
        "thread_b_checkpoint_values": thread_b_state.values,
        "shared_store_items": store_items,
    }


def format_combined_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal artifacts."""

    lines = [
        "# Combined demo",
        "",
        f"Lesson: {story['lesson']}",
        "",
        "thread-b asks in a new thread:",
        f"  {story['thread_b_reply']}",
        "",
        "Checkpoint state is separate:",
        f"  thread-a values: {story['thread_a_checkpoint_values']}",
        f"  thread-b values: {story['thread_b_checkpoint_values']}",
        "",
        "Store memory is shared by namespace:",
    ]
    lines.extend(
        f"  - {item['namespace']} / {item['key']} = {item['value']}"
        for item in story["shared_store_items"]
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_combined_story(run_combined_story()))
