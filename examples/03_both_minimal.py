"""Copy-paste recipe: the production shape — checkpointer AND store together.

The checkpointer keeps per-thread history; the store keeps durable facts that
follow the user into new threads.

Run: python examples/03_both_minimal.py
"""

from __future__ import annotations

from dataclasses import dataclass
from operator import add
from typing import Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict


@dataclass(frozen=True)
class Context:
    user_id: str


class State(TypedDict, total=False):
    user_message: str
    reply: str
    history: Annotated[list[str], add]  # checkpointed: stays inside one thread


def chat_node(state: State, runtime: Runtime[Context]) -> State:
    namespace = (runtime.context.user_id, "profile")
    text = state["user_message"]

    if text.startswith("my name is "):
        name = text.removeprefix("my name is ").strip(" .!")
        runtime.store.put(namespace, "name", {"value": name})  # durable, cross-thread

    stored = runtime.store.get(namespace, "name")
    reply = f"Hi {stored.value['value']}!" if stored else "Hi, who are you?"
    return {"reply": reply, "history": [text]}


def build_graph():
    builder = StateGraph(State, context_schema=Context)
    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)
    return builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())


def main() -> None:
    graph = build_graph()
    ada = Context(user_id="user-ada")
    monday = {"configurable": {"thread_id": "monday-chat"}}
    friday = {"configurable": {"thread_id": "friday-chat"}}

    graph.invoke({"user_message": "my name is Ada"}, monday, context=ada)
    later = graph.invoke({"user_message": "hello again"}, friday, context=ada)

    assert later["reply"] == "Hi Ada!"  # the store remembered across threads
    assert later["history"] == ["hello again"]  # checkpoint history did not leak between threads
    print("friday reply:", later["reply"])
    print("friday history:", later["history"])


if __name__ == "__main__":
    main()
