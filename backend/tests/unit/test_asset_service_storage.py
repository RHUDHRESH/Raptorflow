from __future__ import annotations

import pytest

from backend.core.storage_mgr import StorageManager
from backend.services.asset_service import AssetService


class _FakeBucket:
    def __init__(self, name: str, public: bool) -> None:
        self.name = name
        self.public = public


class _FakeStorageAPI:
    def __init__(self) -> None:
        self.updated = []
        self.created = []
        self._buckets = [_FakeBucket("uploads", public=False)]

    def list_buckets(self):
        return self._buckets

    def update_bucket(self, name: str, payload):
        self.updated.append((name, payload))

    def create_bucket(self, name: str, options):
        self.created.append((name, options))


class _FakeClient:
    def __init__(self) -> None:
        self.storage = _FakeStorageAPI()


class _FakeStorageManager:
    def __init__(self) -> None:
        self.calls = []

    async def create_bucket(self, name: str, public: bool = True) -> bool:
        self.calls.append((name, public))
        return True


@pytest.mark.asyncio
async def test_storage_manager_updates_bucket_visibility() -> None:
    manager = StorageManager("https://example.supabase.co", "service-key")
    manager._client = _FakeClient()  # type: ignore[assignment]

    ok = await manager.create_bucket("uploads", public=True)

    assert ok is True
    fake_storage = manager.client.storage
    assert fake_storage.updated == [("uploads", {"public": True})]
    assert fake_storage.created == []


@pytest.mark.asyncio
async def test_asset_service_ensures_public_bucket() -> None:
    fake_storage = _FakeStorageManager()
    service = AssetService(
        supabase_client=object(),  # type: ignore[arg-type]
        storage_manager=fake_storage,  # type: ignore[arg-type]
        storage_bucket="uploads",
    )

    await service._ensure_bucket()

    assert fake_storage.calls == [("uploads", True)]

