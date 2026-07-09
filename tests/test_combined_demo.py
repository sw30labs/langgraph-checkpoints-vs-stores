from checkpoints_vs_stores.combined_demo import run_combined_story
from checkpoints_vs_stores.demo import collect, render_text


def test_combined_demo_shows_two_persistence_layers() -> None:
    story = run_combined_story()

    assert "Python" in story["thread_b_reply"]
    assert story["thread_a_checkpoint_values"]["user_message"] == "my favorite language is Python"
    assert story["thread_b_checkpoint_values"]["user_message"] == "what language do I like?"
    assert story["shared_store_items"][0]["value"]["value"] == "Python"


def test_cli_collection_and_rendering() -> None:
    results = collect("all")
    rendered = render_text(results)

    assert "# Checkpoint demo" in rendered
    assert "# Store demo" in rendered
    assert "# Combined demo" in rendered
    assert "Ada" in rendered
    assert "Python" in rendered
