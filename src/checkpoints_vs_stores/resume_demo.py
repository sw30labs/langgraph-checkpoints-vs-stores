"""Kill-and-resume demo: persistence that survives process death.

Chapter 1 used ``InMemorySaver``, which forgets everything when the process
exits. This demo runs each half of a conversation in a **separate OS
process** against the same SQLite file: the first process learns a fact and
exits, and a brand-new process (new PID) recalls it by resuming the same
``thread_id`` — something no in-memory checkpointer can do.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from checkpoints_vs_stores.backends import open_checkpointer
from checkpoints_vs_stores.checkpoint_demo import build_checkpoint_graph

THREAD = {"configurable": {"thread_id": "crash-test"}}

PHASE_MESSAGES = {
    1: "hi, my name is Ada",
    2: "what is my name?",
}


def run_phase(phase: int, db_path: str) -> dict[str, Any]:
    """Run one conversation turn against the SQLite file, in this process."""

    with open_checkpointer("sqlite", sqlite_path=db_path) as saver:
        graph = build_checkpoint_graph(saver)
        result = graph.invoke({"user_message": PHASE_MESSAGES[phase]}, THREAD)
        history_len = len(list(graph.get_state_history(THREAD)))
    return {
        "pid": os.getpid(),
        "phase": phase,
        "user_message": PHASE_MESSAGES[phase],
        "reply": result["reply"],
        "checkpoints_in_db": history_len,
    }


def _run_phase_in_subprocess(phase: int, db_path: str) -> dict[str, Any]:
    """Run a phase in a fresh Python process and collect its JSON output."""

    src_dir = str(Path(__file__).resolve().parents[1])
    env = dict(os.environ)
    env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "checkpoints_vs_stores.resume_demo",
            "--phase",
            str(phase),
            "--db",
            db_path,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
        env=env,
    )
    return json.loads(completed.stdout)


def run_resume_story(db_path: str | None = None) -> dict[str, Any]:
    """Run the two-process story and return serializable evidence."""

    if db_path is None:
        db_path = str(Path(tempfile.mkdtemp(prefix="lg-resume-")) / "resume-demo.db")

    first = _run_phase_in_subprocess(1, db_path)
    second = _run_phase_in_subprocess(2, db_path)

    return {
        "lesson": "A durable checkpointer lets a new process resume a thread after a crash.",
        "db_file": Path(db_path).name,
        "phase1": first,
        "phase2": second,
        "different_processes": first["pid"] != second["pid"],
        "orchestrator_pid": os.getpid(),
    }


def format_resume_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    p1, p2 = story["phase1"], story["phase2"]
    lines = [
        "# Kill-and-resume demo (SQLite)",
        "",
        f"Lesson: {story['lesson']}",
        "",
        f"process A (pid {p1['pid']}) says: {p1['user_message']!r}",
        f"  -> {p1['reply']}",
        f"  process A exits. The only survivor is {story['db_file']}.",
        "",
        f"process B (pid {p2['pid']}) asks: {p2['user_message']!r}",
        f"  -> {p2['reply']}",
        "",
        f"different OS processes: {story['different_processes']}",
        f"checkpoints in the SQLite file: {p2['checkpoints_in_db']}",
        "",
        "InMemorySaver could never do this: RAM dies with the process.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Subprocess entry point: run a single phase and print JSON."""

    parser = argparse.ArgumentParser(prog="resume-phase")
    parser.add_argument("--phase", type=int, choices=[1, 2], required=True)
    parser.add_argument("--db", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(run_phase(args.phase, args.db)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
