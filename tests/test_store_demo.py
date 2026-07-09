from checkpoints_vs_stores.store_demo import run_store_story


def test_store_crosses_threads_for_same_user_namespace() -> None:
    story = run_store_story()

    assert "favorite_language=Python" in story["thread_a_reply"]
    assert "Python" in story["thread_b_reply_same_user"]
    assert "Store" in story["thread_b_reply_same_user"]
    assert "don't have" in story["thread_c_reply_different_user"].lower()


def test_store_items_are_key_value_memories() -> None:
    story = run_store_story()
    items = story["user_ada_store_items"]

    assert len(items) == 1
    assert items[0]["namespace"] == ["user-ada", "profile"]
    assert items[0]["key"] == "favorite_language"
    assert items[0]["value"]["value"] == "Python"
    assert story["user_grace_store_items"] == []
