"""Chapter 2: persistence backends, kill-and-resume, peek, and search."""

from __future__ import annotations

import pytest

from checkpoints_vs_stores.backends import server_reachable
from checkpoints_vs_stores.matrix_demo import run_matrix_story
from checkpoints_vs_stores.peek_demo import run_peek_story
from checkpoints_vs_stores.resume_demo import run_resume_story
from checkpoints_vs_stores.search_demo import run_search_story


def test_resume_survives_process_death() -> None:
    story = run_resume_story()

    assert story["different_processes"], "phases must run in separate OS processes"
    assert story["phase1"]["pid"] != story["orchestrator_pid"]
    assert "Ada" in story["phase2"]["reply"]
    assert story["phase2"]["checkpoints_in_db"] >= 2


def test_peek_shows_opaque_checkpoints_and_readable_store_rows() -> None:
    story = run_peek_story()

    assert "checkpoints" in story["tables"]
    assert "store" in story["tables"]
    assert story["checkpoint_row_count"] >= 2
    assert all(row["type"] == "msgpack" for row in story["checkpoint_rows"])
    assert story["checkpoint_blob_preview"].startswith("b'")

    store_row = story["store_rows"][0]
    assert store_row["key"] == "favorite_language"
    assert store_row["value"]["value"] == "Python"


def test_search_ranks_memories_by_meaning() -> None:
    story = run_search_story()

    for result in story["results"]:
        assert result["top_key"] == result["expected_key"], result["query"]
        assert result["top_score"] > 0


def test_matrix_local_backends_roundtrip() -> None:
    story = run_matrix_story(backends=("memory", "sqlite"))

    assert all(row["status"] == "ok" for row in story["rows"])
    assert all("Python" in row["recall_reply"] for row in story["rows"])
    assert story["ok_count"] == 2


@pytest.mark.skipif(
    not server_reachable("postgres"), reason="postgres not running (docker compose up -d)"
)
def test_matrix_postgres_roundtrip() -> None:
    story = run_matrix_story(backends=("postgres",))

    assert story["rows"][0]["status"] == "ok", story["rows"][0]
    assert "Python" in story["rows"][0]["recall_reply"]


@pytest.mark.skipif(
    not server_reachable("redis"), reason="redis not running (docker compose up -d)"
)
def test_matrix_redis_roundtrip() -> None:
    story = run_matrix_story(backends=("redis",))

    assert story["rows"][0]["status"] == "ok", story["rows"][0]
    assert "Python" in story["rows"][0]["recall_reply"]
