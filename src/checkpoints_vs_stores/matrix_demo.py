"""Backend matrix demo: the same graph code runs on all four backends.

For each backend this compiles the Chapter 1 store graph with that backend's
checkpointer and store, writes a memory in one thread, and recalls it from a
second thread. The graph code never changes — only the factory call does.
Unreachable servers are reported, not treated as failures: postgres and redis
need ``docker compose up -d``.
"""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph

from checkpoints_vs_stores.backends import BACKENDS, open_checkpointer, open_store, server_reachable
from checkpoints_vs_stores.store_demo import MemoryState, UserContext, memory_node

RECOMMENDATIONS = {
    "memory": "dev & tests: zero setup, gone on restart",
    "sqlite": "local apps & PoCs: one durable file, no server",
    "postgres": "production default: one database for both layers",
    "redis": "low latency / native TTLs: needs Redis 8+ (JSON + search)",
}


def _run_roundtrip(backend: str, sqlite_path: str) -> dict[str, Any]:
    """Write a memory in one thread, recall it from another, on one backend."""

    run_id = uuid.uuid4().hex[:8]  # isolate reruns against persistent servers
    user = UserContext(user_id=f"user-{run_id}")
    thread_a = {"configurable": {"thread_id": f"a-{run_id}"}}
    thread_b = {"configurable": {"thread_id": f"b-{run_id}"}}

    with (
        open_checkpointer(backend, sqlite_path=sqlite_path) as saver,
        open_store(backend, sqlite_path=sqlite_path) as store,
    ):
        builder = StateGraph(MemoryState, context_schema=UserContext)
        builder.add_node("memory_node", memory_node)
        builder.add_edge(START, "memory_node")
        builder.add_edge("memory_node", END)
        graph = builder.compile(checkpointer=saver, store=store)

        graph.invoke({"user_message": "my favorite language is Python"}, thread_a, context=user)
        recalled = graph.invoke(
            {"user_message": "what language do I like?"}, thread_b, context=user
        )

    return {"recall_reply": recalled["reply"], "recalled_python": "Python" in recalled["reply"]}


def run_matrix_story(backends: tuple[str, ...] = BACKENDS) -> dict[str, Any]:
    """Try the same write/recall round-trip on every requested backend."""

    tmp = Path(tempfile.mkdtemp(prefix="lg-matrix-"))
    rows: list[dict[str, Any]] = []
    for backend in backends:
        row: dict[str, Any] = {
            "backend": backend,
            "recommended_for": RECOMMENDATIONS[backend],
        }
        if not server_reachable(backend):
            row.update(
                status="unreachable",
                detail="server not running - start it with: docker compose up -d",
            )
        else:
            try:
                result = _run_roundtrip(backend, sqlite_path=str(tmp / f"{backend}.db"))
                row.update(status="ok" if result["recalled_python"] else "failed", **result)
            except Exception as error:  # pragma: no cover - depends on live servers
                row.update(status="error", detail=f"{type(error).__name__}: {error}")
        rows.append(row)

    return {
        "lesson": "Swapping backends is a one-line change: the graph code is identical.",
        "rows": rows,
        "ok_count": sum(1 for row in rows if row["status"] == "ok"),
    }


def format_matrix_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    lines = [
        "# Backend matrix",
        "",
        f"Lesson: {story['lesson']}",
        "",
    ]
    for row in story["rows"]:
        status = row["status"]
        lines.append(f"{row['backend']:<9} {status:<12} {row['recommended_for']}")
        if status == "ok":
            lines.append(f"          recall across threads: {row['recall_reply']}")
        elif "detail" in row:
            lines.append(f"          {row['detail']}")
    lines.extend(
        ["", f"{story['ok_count']}/{len(story['rows'])} backends completed the round-trip."]
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_matrix_story(run_matrix_story()))
