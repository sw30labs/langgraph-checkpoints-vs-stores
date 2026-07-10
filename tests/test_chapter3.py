"""Chapter 3: human-in-the-loop interrupts and time travel."""

from __future__ import annotations

from checkpoints_vs_stores.hitl_demo import run_hitl_story
from checkpoints_vs_stores.timetravel_demo import run_timetravel_story


def test_hitl_pauses_and_resumes_across_runtimes() -> None:
    story = run_hitl_story()

    approved, rejected = story["approved"], story["rejected"]
    assert approved["interrupt_question"] == "Approve refund of $120?"
    assert approved["paused_before"] == ["approval_gate"]
    assert approved["decision"] == "approved"
    assert approved["outcome"] == "refunded $120"
    assert rejected["decision"] == "rejected"
    assert "cancelled" in rejected["outcome"]


def test_hitl_resume_reexecutes_the_interrupted_node() -> None:
    story = run_hitl_story()

    # Documented behavior: the node body runs once to pause, then again in
    # full on resume - the reason pre-interrupt side effects must be idempotent.
    assert story["approved"]["gate_entries"] == 2
    assert story["rejected"]["gate_entries"] == 2
    assert story["gate_reexecuted"]


def test_timetravel_replay_reproduces_the_past() -> None:
    story = run_timetravel_story()

    assert story["replay_matches_original"]
    assert "Ada" in story["replayed_reply"]


def test_timetravel_fork_creates_second_timeline() -> None:
    story = run_timetravel_story()

    assert "Grace" in story["forked_reply"]
    assert story["forked_facts"] == ["name=Ada", "name=Grace"]
    assert story["branches_recorded"]
    assert "Ada" in story["original_reply"]  # the original timeline is intact
