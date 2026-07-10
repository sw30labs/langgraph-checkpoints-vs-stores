"""Semantic search demo: query store memories by meaning, fully offline.

Real deployments configure the store's ``index`` with an embedding model
(e.g. OpenAI or a local model) so ``store.search(..., query=...)`` ranks
memories by similarity. To stay deterministic and API-key-free, this demo
uses a toy bag-of-character-trigrams embedding — crude, but enough to rank
lexically related memories first, and the Store API is byte-for-byte the one
you would use in production.
"""

from __future__ import annotations

import hashlib
from typing import Any

from checkpoints_vs_stores.backends import open_store

EMBED_DIMS = 64

MEMORIES = {
    "language": {"text": "user loves Python for building data pipelines"},
    "editor": {"text": "user's favorite editor is neovim with plugins"},
    "pet": {"text": "the user's cat is named Turing"},
}

QUERIES = {
    "which programming language does the user love for pipelines?": "language",
    "what is the user's cat called?": "pet",
}


def trigram_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic toy embedding: hashed character trigrams, L2-normalized.

    Production swap: replace this callable with a real embedding model; the
    index config and search calls stay identical.
    """

    vectors: list[list[float]] = []
    for text in texts:
        vector = [0.0] * EMBED_DIMS
        lowered = text.lower()
        for i in range(max(len(lowered) - 2, 0)):
            trigram = lowered[i : i + 3]
            digest = hashlib.md5(trigram.encode()).hexdigest()
            vector[int(digest, 16) % EMBED_DIMS] += 1.0
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        vectors.append([value / norm for value in vector])
    return vectors


def run_search_story() -> dict[str, Any]:
    """Store a few memories, then retrieve them by natural-language query."""

    namespace = ("user-ada", "memories")
    results: list[dict[str, Any]] = []

    with open_store("sqlite", index={"embed": trigram_embed, "dims": EMBED_DIMS}) as store:
        for key, value in MEMORIES.items():
            store.put(namespace, key, value)

        for query, expected_key in QUERIES.items():
            hits = store.search(namespace, query=query, limit=len(MEMORIES))
            results.append(
                {
                    "query": query,
                    "expected_key": expected_key,
                    "ranked_keys": [hit.key for hit in hits],
                    "top_key": hits[0].key,
                    "top_text": hits[0].value["text"],
                    "top_score": round(hits[0].score, 3),
                }
            )

    return {
        "lesson": "Stores can rank memories by meaning: index config + store.search(query=...).",
        "memory_count": len(MEMORIES),
        "results": results,
        "disclaimer": "Toy trigram embeddings keep this offline; use a real model in production.",
    }


def format_search_story(story: dict[str, Any]) -> str:
    """Human-friendly text version for terminal output."""

    lines = [
        "# Semantic search demo (store index)",
        "",
        f"Lesson: {story['lesson']}",
        "",
        f"{story['memory_count']} memories stored for user-ada. Queries:",
    ]
    for result in story["results"]:
        lines.extend(
            [
                "",
                f"Q: {result['query']}",
                f"  top hit: {result['top_key']} (score {result['top_score']})",
                f"  -> {result['top_text']}",
            ]
        )
    lines.extend(["", f"Note: {story['disclaimer']}"])
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(format_search_story(run_search_story()))
