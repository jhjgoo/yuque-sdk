"""Tests for cache manager."""

import asyncio

import pytest

from yuque.cache.manager import AsyncCacheManager, CacheManager, DEFAULT_TTL, TTL_POLICIES
from yuque.cache.memory import MemoryCacheBackend


class TestCacheManagerInit:
    """Test CacheManager initialization."""

    def test_init_default(self):
        manager = CacheManager()
        assert manager._backend is not None
        assert manager._enabled is True
        assert manager._default_ttl == DEFAULT_TTL

    def test_init_with_backend(self):
        backend = MemoryCacheBackend(max_size=500)
        manager = CacheManager(backend=backend)
        assert manager.backend == backend

    def test_init_disabled(self):
        manager = CacheManager(enabled=False)
        assert manager.enabled is False

    def test_init_custom_ttl_policies(self):
        custom_policies = {"/custom": 100}
        manager = CacheManager(ttl_policies=custom_policies)
        assert manager._ttl_policies["/custom"] == 100

    def test_init_custom_default_ttl(self):
        manager = CacheManager(default_ttl=7200)
        assert manager._default_ttl == 7200


class TestCacheManagerProperties:
    """Test CacheManager properties."""

    def test_backend_property(self):
        backend = MemoryCacheBackend()
        manager = CacheManager(backend=backend)
        assert manager.backend == backend

    def test_stats_property(self):
        manager = CacheManager()
        stats = manager.stats
        assert stats is not None

    def test_enabled_property(self):
        manager = CacheManager()
        assert manager.enabled is True

        manager.enabled = False
        assert manager.enabled is False

        manager.enabled = True
        assert manager.enabled is True


class TestCacheManagerGetTTL:
    """Test get_ttl_for_endpoint method."""

    def test_get_ttl_user_endpoint(self):
        manager = CacheManager()
        ttl = manager.get_ttl_for_endpoint("/user")
        assert ttl == TTL_POLICIES["/user"]

    def test_get_ttl_repos_endpoint(self):
        manager = CacheManager()
        ttl = manager.get_ttl_for_endpoint("/repos")
        assert ttl == TTL_POLICIES["/repos"]

    def test_get_ttl_docs_endpoint(self):
        manager = CacheManager()
        ttl = manager.get_ttl_for_endpoint("/docs/123")
        assert ttl == TTL_POLICIES["/docs/"]

    def test_get_ttl_search_endpoint(self):
        manager = CacheManager()
        ttl = manager.get_ttl_for_endpoint("/search")
        assert ttl == TTL_POLICIES["/search"]

    def test_get_ttl_unknown_endpoint(self):
        manager = CacheManager()
        ttl = manager.get_ttl_for_endpoint("/unknown")
        assert ttl == DEFAULT_TTL

    def test_get_ttl_custom_policy(self):
        custom_policies = {"/repos": 100}
        manager = CacheManager(ttl_policies=custom_policies)
        ttl = manager.get_ttl_for_endpoint("/repos")
        assert ttl == 100


class TestCacheManagerGet:
    """Test CacheManager get method."""

    def test_get_existing_key(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"})

        result = manager.get("/test")
        assert result == {"data": "value"}

    def test_get_nonexistent_key(self):
        manager = CacheManager()
        result = manager.get("/nonexistent")
        assert result is None

    def test_get_with_params(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"}, params={"id": 123})

        result = manager.get("/test", params={"id": 123})
        assert result == {"data": "value"}

    def test_get_with_different_params(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value1"}, params={"id": 1})
        manager.set("/test", {"data": "value2"}, params={"id": 2})

        result1 = manager.get("/test", params={"id": 1})
        result2 = manager.get("/test", params={"id": 2})

        assert result1 == {"data": "value1"}
        assert result2 == {"data": "value2"}

    def test_get_when_disabled(self):
        manager = CacheManager(enabled=False)
        manager.set("/test", {"data": "value"})

        result = manager.get("/test")
        assert result is None

    def test_get_non_dict_value(self):
        manager = CacheManager()
        manager._backend.set("yuque:/test", "string_value")

        result = manager.get("/test")
        assert result == {"data": "string_value"}

    def test_get_records_hit_stats(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"})

        initial_stats = manager.stats
        manager.get("/test")
        final_stats = manager.stats

        assert final_stats.hits > initial_stats.hits

    def test_get_records_miss_stats(self):
        manager = CacheManager()

        initial_stats = manager.stats
        manager.get("/nonexistent")
        final_stats = manager.stats

        assert final_stats.misses > initial_stats.misses


class TestCacheManagerSet:
    """Test CacheManager set method."""

    def test_set_basic(self):
        manager = CacheManager()
        result = manager.set("/test", {"data": "value"})
        assert result is True

        retrieved = manager.get("/test")
        assert retrieved == {"data": "value"}

    def test_set_with_custom_ttl(self):
        manager = CacheManager()
        result = manager.set("/test", {"data": "value"}, ttl=100)
        assert result is True

    def test_set_with_auto_ttl(self):
        manager = CacheManager()
        result = manager.set("/user", {"data": "value"})
        assert result is True

    def test_set_when_disabled(self):
        manager = CacheManager(enabled=False)
        result = manager.set("/test", {"data": "value"})
        assert result is False

    def test_set_with_params(self):
        manager = CacheManager()
        result = manager.set("/test", {"data": "value"}, params={"id": 123})
        assert result is True

        retrieved = manager.get("/test", params={"id": 123})
        assert retrieved == {"data": "value"}

    def test_set_records_stats(self):
        manager = CacheManager()

        initial_stats = manager.stats
        manager.set("/test", {"data": "value"})
        final_stats = manager.stats

        assert final_stats.sets > initial_stats.sets


class TestCacheManagerDelete:
    """Test CacheManager delete method."""

    def test_delete_existing(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"})

        result = manager.delete("/test")
        assert result is True

        assert manager.get("/test") is None

    def test_delete_nonexistent(self):
        manager = CacheManager()
        result = manager.delete("/nonexistent")
        assert result is False

    def test_delete_when_disabled(self):
        manager = CacheManager(enabled=False)
        manager.set("/test", {"data": "value"})

        result = manager.delete("/test")
        assert result is False

    def test_delete_with_params(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"}, params={"id": 123})

        result = manager.delete("/test", params={"id": 123})
        assert result is True

    def test_delete_records_stats(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"})

        initial_stats = manager.stats
        manager.delete("/test")
        final_stats = manager.stats

        assert final_stats.deletes > initial_stats.deletes


class TestCacheManagerInvalidatePattern:
    """Test invalidate_pattern method."""

    def test_invalidate_pattern_basic(self):
        manager = CacheManager()
        count = manager.invalidate_pattern("/docs")
        assert count >= 0

    def test_invalidate_pattern_no_match(self):
        manager = CacheManager()
        count = manager.invalidate_pattern("/nonexistent")
        assert count == 0


class TestCacheManagerClear:
    """Test clear method."""

    def test_clear_empty(self):
        manager = CacheManager()
        manager.clear()

        assert manager.backend.get_size() == 0

    def test_clear_with_entries(self):
        manager = CacheManager()
        manager.set("/test1", {"data": "value1"})
        manager.set("/test2", {"data": "value2"})

        manager.clear()

        assert manager.backend.get_size() == 0
        assert manager.get("/test1") is None
        assert manager.get("/test2") is None


class TestCacheManagerStats:
    """Test statistics methods."""

    def test_get_stats_dict(self):
        manager = CacheManager()
        stats_dict = manager.get_stats_dict()

        assert "hits" in stats_dict
        assert "misses" in stats_dict
        assert "sets" in stats_dict
        assert "deletes" in stats_dict

    def test_reset_stats(self):
        manager = CacheManager()
        manager.set("/test", {"data": "value"})
        manager.get("/test")
        manager.get("/nonexistent")

        manager.reset_stats()
        stats = manager.stats

        assert stats.hits == 0
        assert stats.misses == 0


class TestAsyncCacheManagerInit:
    """Test AsyncCacheManager initialization."""

    def test_init_default(self):
        manager = AsyncCacheManager()
        assert manager._sync_manager is not None
        assert manager.enabled is True

    def test_init_with_backend(self):
        backend = MemoryCacheBackend()
        manager = AsyncCacheManager(backend=backend)
        assert manager.backend == backend

    def test_init_disabled(self):
        manager = AsyncCacheManager(enabled=False)
        assert manager.enabled is False


class TestAsyncCacheManagerProperties:
    """Test AsyncCacheManager properties."""

    def test_backend_property(self):
        backend = MemoryCacheBackend()
        manager = AsyncCacheManager(backend=backend)
        assert manager.backend == backend

    def test_stats_property(self):
        manager = AsyncCacheManager()
        stats = manager.stats
        assert stats is not None

    def test_enabled_property(self):
        manager = AsyncCacheManager()
        assert manager.enabled is True

        manager.enabled = False
        assert manager.enabled is False

    def test_get_ttl_for_endpoint(self):
        manager = AsyncCacheManager()
        ttl = manager.get_ttl_for_endpoint("/user")
        assert ttl == TTL_POLICIES["/user"]


class TestAsyncCacheManagerGet:
    """Test AsyncCacheManager get method."""

    @pytest.mark.asyncio
    async def test_get_existing_key(self):
        manager = AsyncCacheManager()
        await manager.set("/test", {"data": "value"})

        result = await manager.get("/test")
        assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        manager = AsyncCacheManager()
        result = await manager.get("/nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_when_disabled(self):
        manager = AsyncCacheManager(enabled=False)
        await manager.set("/test", {"data": "value"})

        result = await manager.get("/test")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_with_params(self):
        manager = AsyncCacheManager()
        await manager.set("/test", {"data": "value"}, params={"id": 123})

        result = await manager.get("/test", params={"id": 123})
        assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_get_records_stats(self):
        manager = AsyncCacheManager()
        await manager.set("/test", {"data": "value"})

        initial_stats = manager.stats
        await manager.get("/test")
        final_stats = manager.stats

        assert final_stats.hits > initial_stats.hits


class TestAsyncCacheManagerSet:
    """Test AsyncCacheManager set method."""

    @pytest.mark.asyncio
    async def test_set_basic(self):
        manager = AsyncCacheManager()
        result = await manager.set("/test", {"data": "value"})
        assert result is True

        retrieved = await manager.get("/test")
        assert retrieved == {"data": "value"}

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self):
        manager = AsyncCacheManager()
        result = await manager.set("/test", {"data": "value"}, ttl=100)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_when_disabled(self):
        manager = AsyncCacheManager(enabled=False)
        result = await manager.set("/test", {"data": "value"})
        assert result is False

    @pytest.mark.asyncio
    async def test_set_records_stats(self):
        manager = AsyncCacheManager()

        initial_stats = manager.stats
        await manager.set("/test", {"data": "value"})
        final_stats = manager.stats

        assert final_stats.sets > initial_stats.sets


class TestAsyncCacheManagerDelete:
    """Test AsyncCacheManager delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing(self):
        manager = AsyncCacheManager()
        await manager.set("/test", {"data": "value"})

        result = await manager.delete("/test")
        assert result is True

        assert await manager.get("/test") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        manager = AsyncCacheManager()
        result = await manager.delete("/nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_when_disabled(self):
        manager = AsyncCacheManager(enabled=False)
        await manager.set("/test", {"data": "value"})

        result = await manager.delete("/test")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_records_stats(self):
        manager = AsyncCacheManager()
        await manager.set("/test", {"data": "value"})

        initial_stats = manager.stats
        await manager.delete("/test")
        final_stats = manager.stats

        assert final_stats.deletes > initial_stats.deletes


class TestAsyncCacheManagerClear:
    """Test AsyncCacheManager clear method."""

    @pytest.mark.asyncio
    async def test_clear_empty(self):
        manager = AsyncCacheManager()
        await manager.clear()

        assert manager.backend.get_size() == 0

    @pytest.mark.asyncio
    async def test_clear_with_entries(self):
        manager = AsyncCacheManager()
        await manager.set("/test1", {"data": "value1"})
        await manager.set("/test2", {"data": "value2"})

        await manager.clear()

        assert manager.backend.get_size() == 0

    @pytest.mark.asyncio
    async def test_close_with_backend_support(self):
        manager = AsyncCacheManager()
        await manager.close()


class TestAsyncCacheManagerStats:
    """Test AsyncCacheManager statistics methods."""

    def test_get_stats_dict(self):
        manager = AsyncCacheManager()
        stats_dict = manager.get_stats_dict()

        assert "hits" in stats_dict
        assert "misses" in stats_dict

    def test_reset_stats(self):
        manager = AsyncCacheManager()

        manager.reset_stats()
        stats = manager.stats

        assert stats.hits == 0
        assert stats.misses == 0


class TestCacheManagerErrorHandling:
    """Test error handling in CacheManager."""

    def test_get_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def get(self, key):
                raise Exception("Backend error")

        manager = CacheManager(backend=FailingBackend())
        result = manager.get("/test")
        assert result is None

    def test_set_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def set(self, key, value, ttl_seconds=None):
                raise Exception("Backend error")

        manager = CacheManager(backend=FailingBackend())
        result = manager.set("/test", {"data": "value"})
        assert result is False

    def test_delete_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def delete(self, key):
                raise Exception("Backend error")

        manager = CacheManager(backend=FailingBackend())
        result = manager.delete("/test")
        assert result is False

    def test_clear_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def clear(self):
                raise Exception("Backend error")

        manager = CacheManager(backend=FailingBackend())
        manager.clear()

    @pytest.mark.asyncio
    async def test_async_get_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def get(self, key):
                raise Exception("Backend error")

        manager = AsyncCacheManager(backend=FailingBackend())
        result = await manager.get("/test")
        assert result is None

    @pytest.mark.asyncio
    async def test_async_set_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def set(self, key, value, ttl_seconds=None):
                raise Exception("Backend error")

        manager = AsyncCacheManager(backend=FailingBackend())
        result = await manager.set("/test", {"data": "value"})
        assert result is False

    @pytest.mark.asyncio
    async def test_async_delete_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def delete(self, key):
                raise Exception("Backend error")

        manager = AsyncCacheManager(backend=FailingBackend())
        result = await manager.delete("/test")
        assert result is False

    @pytest.mark.asyncio
    async def test_async_clear_handles_backend_error(self):
        class FailingBackend(MemoryCacheBackend):
            def clear(self):
                raise Exception("Backend error")

        manager = AsyncCacheManager(backend=FailingBackend())
        await manager.clear()


class TestCacheManagerIntegration:
    """Integration tests for CacheManager."""

    def test_full_lifecycle(self):
        manager = CacheManager()

        manager.set("/user", {"id": 1, "name": "Test"})
        assert manager.get("/user") == {"id": 1, "name": "Test"}

        manager.set("/user", {"id": 1, "name": "Updated"})
        assert manager.get("/user") == {"id": 1, "name": "Updated"}

        assert manager.delete("/user") is True
        assert manager.get("/user") is None

    def test_multiple_endpoints(self):
        manager = CacheManager()

        manager.set("/user", {"id": 1})
        manager.set("/repos", {"repos": []})
        manager.set("/docs/1", {"doc": "content"})

        assert manager.get("/user") == {"id": 1}
        assert manager.get("/repos") == {"repos": []}
        assert manager.get("/docs/1") == {"doc": "content"}

    @pytest.mark.asyncio
    async def test_async_full_lifecycle(self):
        manager = AsyncCacheManager()

        await manager.set("/user", {"id": 1, "name": "Test"})
        assert await manager.get("/user") == {"id": 1, "name": "Test"}

        await manager.set("/user", {"id": 1, "name": "Updated"})
        assert await manager.get("/user") == {"id": 1, "name": "Updated"}

        assert await manager.delete("/user") is True
        assert await manager.get("/user") is None

    @pytest.mark.asyncio
    async def test_async_concurrent_operations(self):
        manager = AsyncCacheManager()

        async def set_and_get(key, value):
            await manager.set(key, value)
            return await manager.get(key)

        results = await asyncio.gather(
            set_and_get("/test1", {"data": "value1"}),
            set_and_get("/test2", {"data": "value2"}),
            set_and_get("/test3", {"data": "value3"}),
        )

        assert results[0] == {"data": "value1"}
        assert results[1] == {"data": "value2"}
        assert results[2] == {"data": "value3"}
