from checkpoints_vs_stores.checkpoint_demo import run_checkpoint_story


def test_checkpoint_recalls_only_inside_same_thread() -> None:
    story = run_checkpoint_story()

    assert "Ada" in story["thread_alpha_second_reply"]
    assert "checkpoint" in story["thread_alpha_second_reply"]
    assert "don't know" in story["thread_fresh_reply"].lower()
    assert story["thread_alpha_facts"] == ["name=Ada"]


def test_checkpoint_history_is_materialized() -> None:
    story = run_checkpoint_story()

    assert story["thread_alpha_checkpoint_count"] >= 2
    assert story["latest_checkpoint_id"]
    assert story["thread_alpha_timeline"][-1].startswith("BOT:")
