from __future__ import annotations

from fnmatch import fnmatch
from typing import Any, Dict

import pytest

from backend.infrastructure.cache import decorator as cache_decorator
from backend.services import cached_queries


class _FakeRedis:
    def __init__(self) -> None:
        self.store: Dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self.store[key] = value

    def keys(self, pattern: str) -> list[str]:
        return [key for key in self.store if fnmatch(key, pattern)]

    def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                deleted += 1
        return deleted


class _FakeQuery:
    def __init__(self) -> None:
        self._id: str | None = None

    def select(self, *_args: Any, **_kwargs: Any) -> "_FakeQuery":
        return self

    def eq(self, column: str, value: str) -> "_FakeQuery":
        if column == "id":
            self._id = value
        return self

    def execute(self) -> Any:
        return type("Result", (), {"data": [{"id": self._id, "name": "Workspace"}]})()


class _FakeSupabase:
    def table(self, _name: str) -> _FakeQuery:
        return _FakeQuery()


@pytest.mark.asyncio
async def test_workspace_cache_invalidation_matches_workspace_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = _FakeRedis()
    monkeypatch.setattr(cache_decorator, "get_redis_client", lambda: redis)
    monkeypatch.setattr(cached_queries, "get_supabase_client", lambda: _FakeSupabase())

    workspace_id = "ws-cache-123"
    row = await cached_queries.get_workspace_by_id(workspace_id)

    assert row is not None
    assert row["id"] == workspace_id
    assert any(workspace_id in key for key in redis.store)

    await cached_queries.invalidate_workspace_cache(workspace_id)

    assert redis.store == {}
