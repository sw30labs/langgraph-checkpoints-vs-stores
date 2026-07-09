"""Copy-paste recipe: thread-scoped memory with a checkpointer.

Run: python examples/01_checkpointer_minimal.py
"""

from __future__ import annotations

from operator import add
from typing import Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    user_message: str
    history: Annotated[list[str], add]  # reducer: each invoke appends instead of replacing


def chat_node(state: State) -> State:
    return {"history": [state["user_message"]]}


def build_graph():
    builder = StateGraph(State)
    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)
    # The only change vs a stateless graph: pass a checkpointer at compile time.
    # Production: swap InMemorySaver for SqliteSaver or PostgresSaver.
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    thread_1 = {"configurable": {"thread_id": "thread-1"}}  # the checkpoint scope key
    thread_2 = {"configurable": {"thread_id": "thread-2"}}

    graph.invoke({"user_message": "hello"}, thread_1)
    result = graph.invoke({"user_message": "still with me?"}, thread_1)
    assert result["history"] == ["hello", "still with me?"]  # resumed from the checkpoint
    print("thread-1 history:", result["history"])

    fresh = graph.invoke({"user_message": "have we met?"}, thread_2)
    assert fresh["history"] == ["have we met?"]  # a new thread_id starts clean
    print("thread-2 history:", fresh["history"])


if __name__ == "__main__":
    main()
