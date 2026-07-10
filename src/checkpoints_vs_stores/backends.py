"""Chapter 2 backend factory: one graph, four persistence backends.

Every checkpointer implements ``BaseCheckpointSaver`` and every store
implements ``BaseStore``, so swapping backends never touches graph code —
only this factory. ``memory`` and ``sqlite`` work out of the box; ``postgres``
and ``redis`` expect the servers from ``docker-compose.yml``.
"""

from __future__ import annotations

import os
import socket
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from urllib.parse import urlparse

BACKENDS = ("memory", "sqlite", "postgres", "redis")

# Non-standard host ports so the demo containers never clash with local servers.
DEFAULT_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5442/postgres"
DEFAULT_REDIS_URL = "redis://localhost:6390"


def postgres_url() -> str:
    return os.environ.get("LG_DEMO_POSTGRES_URL", DEFAULT_POSTGRES_URL)


def redis_url() -> str:
    return os.environ.get("LG_DEMO_REDIS_URL", DEFAULT_REDIS_URL)


def server_reachable(backend: str, timeout: float = 1.0) -> bool:
    """Cheap TCP probe so demos and tests can skip unreachable backends fast."""

    if backend in {"memory", "sqlite"}:
        return True
    url = urlparse(postgres_url() if backend == "postgres" else redis_url())
    try:
        with socket.create_connection((url.hostname, url.port), timeout=timeout):
            return True
    except OSError:
        return False


@contextmanager
def open_checkpointer(backend: str, sqlite_path: str = ":memory:") -> Iterator[Any]:
    """Yield a ready-to-use checkpointer for the chosen backend."""

    if backend == "memory":
        from langgraph.checkpoint.memory import InMemorySaver

        yield InMemorySaver()
    elif backend == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver

        with SqliteSaver.from_conn_string(sqlite_path) as saver:
            yield saver
    elif backend == "postgres":
        from langgraph.checkpoint.postgres import PostgresSaver

        with PostgresSaver.from_conn_string(postgres_url()) as saver:
            saver.setup()
            yield saver
    elif backend == "redis":
        from langgraph.checkpoint.redis import RedisSaver

        with RedisSaver.from_conn_string(redis_url()) as saver:
            saver.setup()
            yield saver
    else:
        raise ValueError(f"Unknown backend: {backend!r} (expected one of {BACKENDS})")


@contextmanager
def open_store(
    backend: str, sqlite_path: str = ":memory:", index: dict[str, Any] | None = None
) -> Iterator[Any]:
    """Yield a ready-to-use store for the chosen backend.

    `index` enables semantic search: {"embed": <callable>, "dims": <int>}.
    """

    if backend == "memory":
        from langgraph.store.memory import InMemoryStore

        yield InMemoryStore(index=index)
    elif backend == "sqlite":
        from langgraph.store.sqlite import SqliteStore

        with SqliteStore.from_conn_string(sqlite_path, index=index) as store:
            store.setup()
            yield store
    elif backend == "postgres":
        from langgraph.store.postgres import PostgresStore

        with PostgresStore.from_conn_string(postgres_url(), index=index) as store:
            store.setup()
            yield store
    elif backend == "redis":
        from langgraph.store.redis import RedisStore

        with RedisStore.from_conn_string(redis_url(), index=index) as store:
            store.setup()
            yield store
    else:
        raise ValueError(f"Unknown backend: {backend!r} (expected one of {BACKENDS})")
