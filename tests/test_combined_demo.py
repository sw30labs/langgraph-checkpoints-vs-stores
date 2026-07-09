import io

from rich.console import Console

from checkpoints_vs_stores.combined_demo import run_combined_story
from checkpoints_vs_stores.demo import collect, render_text, render_tui


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


def test_tui_renders_side_by_side_on_wide_terminals() -> None:
    console = Console(width=160, color_system=None, file=io.StringIO())
    render_tui(console, collect("all"))
    lines = console.file.getvalue().splitlines()

    # On a wide console the checkpoint and store frames share the same rows.
    assert any(
        "Checkpoints - thread-scoped" in line and "Stores - cross-thread" in line for line in lines
    )
    assert any("Combined - both layers" in line for line in lines)
    assert any("Which one do I need?" in line for line in lines)


def test_tui_stacks_panels_on_narrow_terminals() -> None:
    console = Console(width=80, color_system=None, file=io.StringIO())
    render_tui(console, collect("all"))
    output = console.file.getvalue()

    assert "Checkpoints - thread-scoped" in output
    assert "Stores - cross-thread" in output
    assert not any(
        "Checkpoints - thread-scoped" in line and "Stores - cross-thread" in line
        for line in output.splitlines()
    )
