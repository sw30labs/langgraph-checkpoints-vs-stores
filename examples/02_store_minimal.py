"""Copy-paste recipe: cross-thread long-term memory with a store.

There is deliberately no checkpointer here, so every invoke is a brand-new
conversation. The store is the only memory that survives.

Run: python examples/02_store_minimal.py
"""

from __future__ import annotations

from dataclasses import dataclass

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict


@dataclass(frozen=True)
class Context:
    """Runtime context; picks which namespace the node reads and writes."""

    user_id: str


class State(TypedDict, total=False):
    user_message: str
    reply: str


def remember_node(state: State, runtime: Runtime[Context]) -> State:
    namespace = (runtime.context.user_id, "profile")
    text = state["user_message"]

    if text.startswith("remember:"):
        runtime.store.put(namespace, "note", {"text": text.removeprefix("remember:").strip()})
        return {"reply": "saved"}

    item = runtime.store.get(namespace, "note")
    return {"reply": item.value["text"] if item else "nothing saved for this user"}


def build_graph():
    builder = StateGraph(State, context_schema=Context)
    builder.add_node("remember", remember_node)
    builder.add_edge(START, "remember")
    builder.add_edge("remember", END)
    # Production: swap InMemoryStore for PostgresStore (optionally with semantic search).
    return builder.compile(store=InMemoryStore())


def main() -> None:
    graph = build_graph()
    ada = Context(user_id="user-ada")

    graph.invoke({"user_message": "remember: loves Python"}, context=ada)
    recalled = graph.invoke({"user_message": "what do you know?"}, context=ada)
    assert recalled["reply"] == "loves Python"  # new conversation, same user namespace
    print("user-ada recalled:", recalled["reply"])

    grace = Context(user_id="user-grace")
    other = graph.invoke({"user_message": "what do you know?"}, context=grace)
    assert other["reply"] == "nothing saved for this user"  # different namespace
    print("user-grace sees:", other["reply"])


if __name__ == "__main__":
    main()
