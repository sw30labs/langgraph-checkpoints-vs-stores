"""Store demo: cross-thread long-term memory.

This module uses a real LangGraph StateGraph and InMemoryStore. The graph is
also compiled with a checkpointer so the example mirrors production patterns:
checkpoints track the active thread, stores track durable memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from operator import add
from typing import Annotated, Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

from checkpoints_vs_stores.utils import extract_after


@dataclass(frozen=True)
class UserContext:
    """Runtime context that chooses the store namespace."""

    user_id: str


class MemoryState(TypedDict, total=False):
    """Graph state for the store demo.

    `thread_notes` is checkpointed and thread-scoped. Store values are external
    and live under a user namespace.
    """

    user_message: str
    reply: str
    thread_notes: Annotated[list[str], add]


def memory_node(state: MemoryState, runtime: Runtime[UserContext]) -> MemoryState:
    """Write or read durable memory using runtime.store."""

    text = state.get("user_message", "")
    namespace = (runtime.context.user_id, "profile")
    favorite_language = extract_after(text, "favorite language is")

    if favorite_language:
        runtime.store.put(
            namespace,
            "favorite_language",
            {
                "value": favorite_language,
                "why": "Captured from an explicit user preference.",
            },
        )
        reply = (
            "Stored long-term memory: "
            f"favorite_language={favorite_language} for user_id={runtime.context.user_id}."
        )
    elif "what" in text.lower() and "language" in text.lower():
        item = runtime.store.get(namespace, "favorite_language")
        reply = (
            f"Your favorite language is {item.value['value']}. "
            "I found that in the Store, not this thread."
            if item
            else "I don't have a favorite language for this user in the Store."
        )
    else:
        reply = "No store action taken."

    return {
        "reply": reply,
        "thread_notes": [f"{runtime.context.user_id}: {text} -> {reply}"],
    }


def build_store_graph():
    """Build a graph compiled with both a checkpointer and a store."""

    builder = StateGraph(MemoryState, context_schema=UserContext)
    builder.add_node("memory_node", memory_node)
    builder.add_edge(START, "memory_node")
    builder.add_edge("memory_node", END)

    checkpointer = InMemorySaver()
    store = InMemoryStore()
    graph = builder.compile(checkpointer=checkpointer, store=store)
    return graph, store


def serialize_store_items(items: list[Any]) -> list[dict[str, Any]]:
    """Convert LangGraph Item objects into JSON-friendly dictionaries."""

    return [
        {
            "namespace": list(item.namespace),
            "key": item.key,
            "value": item.value,
            "created_at": str(item.created_at),
            "updated_at": str(item.updated_at),
            "score": item.score,
        }
        for item in items
    ]


def run_store_story() -> dict[str, Any]:
    """Run the store example and return serializable evidence."""

    graph, store = build_store_graph()
    ada = UserContext(user_id="user-ada")
    grace = UserContext(user_id="user-grace")

    thread_a = {"configurable": {"thread_id": "thread-a"}}
    thread_b = {"configurable": {"thread_id": "thread-b"}}
    thread_c = {"configurable": {"thread_id": "thread-c"}}

    first = graph.invoke(
        {"user_message": "my favorite language is Python"}, thread_a, context=ada
    )
    second_same_user_new_thread = graph.invoke(
        {"user_message": "what language do I like?"}, thread_b, context=ada
    )
    third_different_user = graph.invoke(
        {"user_message": "what language do I like?"}, thread_c, context=grace
    )

    ada_items = store.search(("user-ada", "profile"), limit=10)
    grace_items = store.search(("user-grace", "profile"), limit=10)

    return {
        "lesson": "Stores are cross-thread when the namespace is shared.",
        "thread_a_reply": first["reply"],
        "thread_b_reply_same_user": second_same_user_new_thread["reply"],
        "thread_c_reply_different_user": third_different_user["reply"],
        "user_ada_store_items": serialize_store_items(ada_items),
        "user_grace_store_items": serialize_store_items(grace_items),
        "thread_a_notes": first.get("thread_notes", []),
        "thread_b_notes": second_same_user_new_thread.get("thread_notes", []),
    }


def format_store_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal artifacts."""

    lines = [
        "# Store demo",
        "",
        f"Lesson: {story['lesson']}",
        "",
        "thread-a / user-ada:",
        f"  {story['thread_a_reply']}",
        "",
        "thread-b / user-ada:",
        f"  {story['thread_b_reply_same_user']}",
        "",
        "thread-c / user-grace:",
        f"  {story['thread_c_reply_different_user']}",
        "",
        "user-ada store items:",
    ]
    if story["user_ada_store_items"]:
        for item in story["user_ada_store_items"]:
            lines.append(f"  - {item['namespace']} / {item['key']} = {item['value']}")
    else:
        lines.append("  - none")

    lines.extend(
        [
            "",
            "Thread notes prove thread state is still separate:",
            f"  thread-a notes: {story['thread_a_notes']}",
            f"  thread-b notes: {story['thread_b_notes']}",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_store_story(run_store_story()))
