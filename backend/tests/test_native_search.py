import pytest

from core.search_native import NativeSearch


@pytest.mark.asyncio
async def test_native_search_results():
    """Verify that native search returns structured results."""
    search = NativeSearch()
    results = await search.query("RaptorFlow marketing automation")

    assert isinstance(results, list)
    if len(results) > 0:
        first = results[0]
        assert "title" in first
        assert "url" in first
        assert "snippet" in first


@pytest.mark.asyncio
async def test_native_search_empty():
    """Verify handling of empty queries."""
    search = NativeSearch()
    results = await search.query("")
    assert results == []
