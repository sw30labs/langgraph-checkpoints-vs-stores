"""Human-in-the-loop demo: interrupt(), pause durably, resume with a decision.

``interrupt()`` needs exactly two things — a checkpointer and a ``thread_id``
— which is why approval flows are a checkpoint-powered pattern. The graph
below wants to issue a refund; it pauses for approval, the paused state lands
in SQLite, and a *rebuilt* graph (fresh objects, same file, as after a
restart) resumes it with the human decision.

The demo also proves the documented gotcha most tutorials skip: on resume the
interrupted node re-executes from its start, so side effects placed before
``interrupt()`` must be idempotent. Watch ``gate_entries``.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from checkpoints_vs_stores.backends import open_checkpointer

# Counts how many times the gate node body runs per thread. It lives at
# module level precisely because graph state written before an interrupt is
# not committed - the node never finished.
GATE_ENTRIES: dict[str, int] = {}


class RefundState(TypedDict, total=False):
    request: str
    amount: int
    decision: str
    outcome: str


def parse_request(state: RefundState) -> RefundState:
    """Extract the dollar amount from the request text."""

    amount = int(state["request"].split("$")[1].split()[0])
    return {"amount": amount}


def approval_gate(state: RefundState) -> RefundState:
    """Pause for a human decision before doing anything irreversible."""

    thread_key = f"${state['amount']}"
    GATE_ENTRIES[thread_key] = GATE_ENTRIES.get(thread_key, 0) + 1

    answer = interrupt(
        {
            "question": f"Approve refund of ${state['amount']}?",
            "amount": state["amount"],
        }
    )
    return {"decision": "approved" if answer["approve"] else "rejected"}


def execute_refund(state: RefundState) -> RefundState:
    """The irreversible action, gated behind the approval."""

    if state["decision"] == "approved":
        return {"outcome": f"refunded ${state['amount']}"}
    return {"outcome": "refund cancelled, customer notified"}


def build_refund_graph(checkpointer):
    builder = StateGraph(RefundState)
    builder.add_node("parse_request", parse_request)
    builder.add_node("approval_gate", approval_gate)
    builder.add_node("execute_refund", execute_refund)
    builder.add_edge(START, "parse_request")
    builder.add_edge("parse_request", "approval_gate")
    builder.add_edge("approval_gate", "execute_refund")
    builder.add_edge("execute_refund", END)
    return builder.compile(checkpointer=checkpointer)


def _ask_then_decide(db_path: str, thread_id: str, request: str, approve: bool) -> dict[str, Any]:
    """Pause in one graph instance, resume in a freshly rebuilt one."""

    config = {"configurable": {"thread_id": thread_id}}

    # Runtime 1: the agent asks and pauses. The paused state lives in SQLite.
    with open_checkpointer("sqlite", sqlite_path=db_path) as saver:
        graph = build_refund_graph(saver)
        paused = graph.invoke({"request": request}, config)
        question = paused["__interrupt__"][0].value
        waiting_on = graph.get_state(config).next

    # Runtime 2: fresh saver, fresh graph - as if the process restarted while
    # the approver took their time. Command(resume=...) feeds the decision in.
    with open_checkpointer("sqlite", sqlite_path=db_path) as saver:
        graph = build_refund_graph(saver)
        final = graph.invoke(Command(resume={"approve": approve}), config)

    return {
        "request": request,
        "interrupt_question": question["question"],
        "paused_before": list(waiting_on),
        "resumed_with": {"approve": approve},
        "decision": final["decision"],
        "outcome": final["outcome"],
        "gate_entries": GATE_ENTRIES[f"${final['amount']}"],
    }


def run_hitl_story(db_path: str | None = None) -> dict[str, Any]:
    """Run an approved and a rejected refund and return the evidence."""

    if db_path is None:
        db_path = str(Path(tempfile.mkdtemp(prefix="lg-hitl-")) / "hitl-demo.db")

    GATE_ENTRIES.clear()
    approved = _ask_then_decide(db_path, "refund-120", "refund $120 for order #4242", True)
    rejected = _ask_then_decide(db_path, "refund-999", "refund $999 for order #1337", False)

    return {
        "lesson": "interrupt() = checkpointer + thread_id: pause for approval, resume anytime.",
        "approved": approved,
        "rejected": rejected,
        "gate_reexecuted": approved["gate_entries"] == 2,
    }


def format_hitl_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    lines = ["# Human-in-the-loop demo", "", f"Lesson: {story['lesson']}"]
    for label, case in (("APPROVED", story["approved"]), ("REJECTED", story["rejected"])):
        lines.extend(
            [
                "",
                f"[{label}] agent receives: {case['request']!r}",
                f"  graph pauses before {case['paused_before']} and asks:",
                f"    {case['interrupt_question']!r}",
                "  ...paused state sits in SQLite; the asking runtime is gone...",
                f"  a rebuilt graph resumes with {case['resumed_with']}",
                f"  -> decision={case['decision']}, outcome: {case['outcome']}",
                f"  gate node body ran {case['gate_entries']}x (pause, then resume re-runs it)",
            ]
        )
    lines.extend(
        [
            "",
            "Resume re-executes the interrupted node from its start:",
            "keep side effects before interrupt() idempotent.",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_hitl_story(run_hitl_story()))
