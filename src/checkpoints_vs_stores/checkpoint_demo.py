"""Checkpoint demo: thread-scoped graph state memory.

This module uses a real LangGraph StateGraph and InMemorySaver. It does not use
an LLM, which keeps the demo deterministic and runnable in CI.
"""

from __future__ import annotations

from operator import add
from typing import Annotated, Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from checkpoints_vs_stores.utils import extract_after


class ThreadState(TypedDict, total=False):
    """Graph state saved by the checkpointer.

    `timeline` and `facts` use reducers so each invocation appends new entries
    to the saved thread state instead of replacing the list.
    """

    user_message: str
    timeline: Annotated[list[str], add]
    facts: Annotated[list[str], add]
    reply: str


def remember_in_thread(state: ThreadState) -> ThreadState:
    """Extract facts from the latest message and append them to thread state."""

    text = state.get("user_message", "")
    updates: ThreadState = {"timeline": [f"USER: {text}"]}
    name = extract_after(text, "my name is")
    if name:
        updates["facts"] = [f"name={name}"]
    return updates


def answer_from_thread(state: ThreadState) -> ThreadState:
    """Answer using only facts available in this checkpointed thread."""

    text = state.get("user_message", "")
    facts = state.get("facts", [])
    names = [fact.split("=", 1)[1] for fact in facts if fact.startswith("name=")]

    if "what" in text.lower() and "name" in text.lower():
        reply = (
            f"Your name is {names[-1]}. I know because this thread has a checkpoint."
            if names
            else "I don't know your name in this thread."
        )
    else:
        reply = f"Checkpoint now has {len(facts)} durable-in-thread fact(s)."

    return {"reply": reply, "timeline": [f"BOT: {reply}"]}


def build_checkpoint_graph():
    """Build a graph compiled with an in-memory checkpointer."""

    builder = StateGraph(ThreadState)
    builder.add_node("remember_in_thread", remember_in_thread)
    builder.add_node("answer_from_thread", answer_from_thread)
    builder.add_edge(START, "remember_in_thread")
    builder.add_edge("remember_in_thread", "answer_from_thread")
    builder.add_edge("answer_from_thread", END)
    return builder.compile(checkpointer=InMemorySaver())


def run_checkpoint_story() -> dict[str, Any]:
    """Run the checkpoint example and return serializable evidence."""

    graph = build_checkpoint_graph()
    thread_alpha = {"configurable": {"thread_id": "thread-alpha"}}
    thread_fresh = {"configurable": {"thread_id": "thread-fresh"}}

    first = graph.invoke({"user_message": "hi, my name is Ada"}, thread_alpha)
    second_same_thread = graph.invoke({"user_message": "what is my name?"}, thread_alpha)
    third_new_thread = graph.invoke({"user_message": "what is my name?"}, thread_fresh)

    latest_state = graph.get_state(thread_alpha)
    history = list(graph.get_state_history(thread_alpha))

    return {
        "lesson": "Checkpoints are scoped to a thread_id.",
        "thread_alpha_first_reply": first["reply"],
        "thread_alpha_second_reply": second_same_thread["reply"],
        "thread_fresh_reply": third_new_thread["reply"],
        "thread_alpha_facts": second_same_thread.get("facts", []),
        "thread_alpha_timeline": second_same_thread.get("timeline", []),
        "latest_checkpoint_id": latest_state.config["configurable"]["checkpoint_id"],
        "thread_alpha_checkpoint_count": len(history),
    }


def format_checkpoint_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal artifacts."""

    lines = [
        "# Checkpoint demo",
        "",
        f"Lesson: {story['lesson']}",
        "",
        "thread-alpha / invoke #1:",
        f"  {story['thread_alpha_first_reply']}",
        "",
        "thread-alpha / invoke #2:",
        f"  {story['thread_alpha_second_reply']}",
        "",
        "thread-fresh / invoke #1:",
        f"  {story['thread_fresh_reply']}",
        "",
        f"thread-alpha facts: {story['thread_alpha_facts']}",
        f"thread-alpha checkpoint count: {story['thread_alpha_checkpoint_count']}",
        f"latest checkpoint id: {story['latest_checkpoint_id']}",
        "",
        "Timeline:",
    ]
    lines.extend(f"  - {entry}" for entry in story["thread_alpha_timeline"])
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_checkpoint_story(run_checkpoint_story()))
