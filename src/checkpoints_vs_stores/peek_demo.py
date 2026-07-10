"""Peek demo: what checkpoints and store items actually look like in a database.

Runs the Chapter 1 store scenario against one SQLite file holding both the
checkpointer tables and the store tables, then reads the raw rows back with
plain SQL. The punchline: checkpoint rows are the framework's opaque msgpack
snapshots; store rows are your own readable JSON data model.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.sqlite import SqliteStore

from checkpoints_vs_stores.store_demo import MemoryState, UserContext, memory_node


def _build_graph(saver: SqliteSaver, store: SqliteStore):
    builder = StateGraph(MemoryState, context_schema=UserContext)
    builder.add_node("memory_node", memory_node)
    builder.add_edge(START, "memory_node")
    builder.add_edge("memory_node", END)
    return builder.compile(checkpointer=saver, store=store)


def run_peek_story(db_path: str | None = None) -> dict[str, Any]:
    """Run a conversation, then read the raw database rows back."""

    if db_path is None:
        db_path = str(Path(tempfile.mkdtemp(prefix="lg-peek-")) / "peek-demo.db")

    ada = UserContext(user_id="user-ada")
    with (
        SqliteSaver.from_conn_string(db_path) as saver,
        SqliteStore.from_conn_string(db_path) as store,
    ):
        store.setup()
        graph = _build_graph(saver, store)
        graph.invoke(
            {"user_message": "my favorite language is Python"},
            {"configurable": {"thread_id": "thread-a"}},
            context=ada,
        )
        graph.invoke(
            {"user_message": "what language do I like?"},
            {"configurable": {"thread_id": "thread-b"}},
            context=ada,
        )

    conn = sqlite3.connect(db_path)
    try:
        tables = sorted(
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        )
        checkpoint_rows = [
            {"thread_id": thread_id, "type": type_, "blob_bytes": size}
            for thread_id, type_, size in conn.execute(
                "SELECT thread_id, type, length(checkpoint) FROM checkpoints ORDER BY thread_id"
            )
        ]
        blob = conn.execute("SELECT checkpoint FROM checkpoints LIMIT 1").fetchone()[0]
        store_rows = [
            {"namespace": prefix, "key": key, "value": json.loads(value)}
            for prefix, key, value in conn.execute("SELECT prefix, key, value FROM store")
        ]
    finally:
        conn.close()

    return {
        "lesson": "Checkpoint rows are opaque runtime snapshots; store rows are your data model.",
        "db_file": Path(db_path).name,
        "tables": tables,
        "checkpoint_row_count": len(checkpoint_rows),
        "checkpoint_rows": checkpoint_rows,
        "checkpoint_blob_preview": repr(blob[:32]),
        "store_rows": store_rows,
    }


def format_peek_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    lines = [
        "# Peek inside the database (SQLite)",
        "",
        f"Lesson: {story['lesson']}",
        "",
        f"one file, both layers: {story['db_file']}",
        f"tables: {', '.join(story['tables'])}",
        "",
        f"checkpointer wrote {story['checkpoint_row_count']} checkpoint row(s) "
        "for a two-turn conversation:",
    ]
    lines.extend(
        f"  - thread={row['thread_id']}  type={row['type']}  blob={row['blob_bytes']}B"
        for row in story["checkpoint_rows"]
    )
    lines.extend(
        [
            "",
            "a checkpoint blob starts like this (msgpack, not for humans):",
            f"  {story['checkpoint_blob_preview']}",
            "",
            "the store table holds readable JSON you designed:",
        ]
    )
    lines.extend(
        f"  - {row['namespace']} / {row['key']} = {json.dumps(row['value'])}"
        for row in story["store_rows"]
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_peek_story(run_peek_story()))
