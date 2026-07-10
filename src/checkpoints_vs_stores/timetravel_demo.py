"""Time-travel demo: replay a past checkpoint, or fork it into a new timeline.

Both operations resume from a prior checkpoint of the thread's history:
*replay* re-runs the graph from that point unchanged (nodes before it are not
re-executed - their results are already saved), while *fork* first edits the
past state with ``update_state`` and then runs forward, creating a second
branch on the same thread. Nodes after the checkpoint really do re-execute -
replay is a resume, not a cache read.
"""

from __future__ import annotations

from typing import Any

from checkpoints_vs_stores.checkpoint_demo import build_checkpoint_graph

THREAD = {"configurable": {"thread_id": "time-travel"}}


def _checkpoint_before_answer(graph) -> Any:
    """Find the past checkpoint that is about to answer 'what is my name?'."""

    for snapshot in graph.get_state_history(THREAD):
        if snapshot.next == ("answer_from_thread",) and (
            snapshot.values.get("user_message") == "what is my name?"
        ):
            return snapshot
    raise RuntimeError("expected checkpoint not found in thread history")


def run_timetravel_story() -> dict[str, Any]:
    """Run a conversation, then replay and fork its history."""

    graph = build_checkpoint_graph()
    graph.invoke({"user_message": "hi, my name is Ada"}, THREAD)
    original = graph.invoke({"user_message": "what is my name?"}, THREAD)

    history_before = len(list(graph.get_state_history(THREAD)))
    snapshot = _checkpoint_before_answer(graph)

    # Replay: run forward from the past checkpoint with nothing changed.
    replayed = graph.invoke(None, snapshot.config)

    # Fork: edit the past (the `facts` reducer appends, so Grace wins as the
    # latest fact), then run forward on the new branch.
    forked_config = graph.update_state(snapshot.config, {"facts": ["name=Grace"]})
    forked = graph.invoke(None, forked_config)

    history_after = len(list(graph.get_state_history(THREAD)))

    return {
        "lesson": "Checkpoints are a timeline: replay any step, or fork it with edited state.",
        "original_reply": original["reply"],
        "replayed_reply": replayed["reply"],
        "replay_matches_original": replayed["reply"] == original["reply"],
        "forked_facts": forked["facts"],
        "forked_reply": forked["reply"],
        "checkpoints_before": history_before,
        "checkpoints_after": history_after,
        "branches_recorded": history_after > history_before,
    }


def format_timetravel_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    lines = [
        "# Time-travel demo",
        "",
        f"Lesson: {story['lesson']}",
        "",
        "live run:",
        f"  -> {story['original_reply']}",
        "",
        "replay the checkpoint right before the answer (no edits):",
        f"  -> {story['replayed_reply']}",
        f"  identical to the live run: {story['replay_matches_original']}",
        "",
        "fork the same checkpoint, editing the past (facts += name=Grace):",
        f"  facts on the new branch: {story['forked_facts']}",
        f"  -> {story['forked_reply']}",
        "",
        f"thread history grew from {story['checkpoints_before']} to "
        f"{story['checkpoints_after']} checkpoints: one thread, two timelines.",
        "",
        "Nodes after the chosen checkpoint re-execute (LLM calls included):",
        "replay is a resume, not a cache read.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_timetravel_story(run_timetravel_story()))
