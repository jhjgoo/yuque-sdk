"""Unit tests for cache integration.

Tests:
- Cache decorator functionality
- Cache invalidation patterns
- SDK methods with cache
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from yuque.mcp.cache import (
    CacheManager,
    MemoryCache,
    clear_default_cache,
    cached,
    invalidate_cache,
    generate_cache_key,
)


class TestMemoryCache:
    """Test MemoryCache functionality."""

    def test_set_and_get(self):
        """Test basic set and get operations."""
        cache = MemoryCache(max_size=100, default_ttl=60)

        # Set value
        cache.set("key1", {"data": "value1"})

        # Get value
        result = cache.get("key1")
        assert result == {"data": "value1"}

    def test_cache_miss(self):
        """Test cache miss."""
        cache = MemoryCache()

        result = cache.get("nonexistent")
        assert result is None

    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = MemoryCache(default_ttl=1)  # 1 second TTL

        cache.set("key1", "value1")

        # Immediate get should work
        result = cache.get("key1")
        assert result == "value1"

        # Wait for expiration
        import time

        time.sleep(2)

        # Should be expired now
        result = cache.get("key1")
        assert result is None

    def test_lru_eviction(self):
        """Test LRU eviction."""
        cache = MemoryCache(max_size=3)

        # Add 3 items
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # All should be present
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Add 4th item, should evict key1 (oldest)
        cache.set("key4", "value4")

        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = MemoryCache()

        # Initial stats
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Miss
        cache.get("nonexistent")
        stats = cache.get_stats()
        assert stats["misses"] == 1

        # Set and hit
        cache.set("key1", "value1")
        cache.get("key1")
        stats = cache.get_stats()
        assert stats["hits"] == 1


class TestCacheManager:
    """Test CacheManager functionality."""

    def setup_method(self):
        """Setup for each test."""
        clear_default_cache()

    def test_singleton_pattern(self):
        """Test get_default_cache returns singleton."""
        from yuque.mcp.cache import get_default_cache

        cache1 = get_default_cache()
        cache2 = get_default_cache()

        assert cache1 is cache2

    def test_smart_ttl(self):
        """Test smart TTL based on endpoint."""
        cache = CacheManager()

        # User endpoint - 24 hours
        ttl = cache.get_ttl_for_endpoint("/user/me")
        assert ttl == 24 * 60 * 60

        # Repo endpoint - 12 hours
        ttl = cache.get_ttl_for_endpoint("/repos/123")
        assert ttl == 12 * 60 * 60

        # Doc endpoint - 3 hours
        ttl = cache.get_ttl_for_endpoint("/docs/123")
        assert ttl == 3 * 60 * 60

        # Search endpoint - 1 hour
        ttl = cache.get_ttl_for_endpoint("/search")
        assert ttl == 1 * 60 * 60

    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = CacheManager.generate_cache_key("/user/me")
        assert "yuque:/user/me" in key1

        key2 = CacheManager.generate_cache_key("/repos/123", params={"format": "markdown"})
        assert "yuque" in key2
        assert "/repos/123" in key2

    def test_pattern_invalidation(self):
        """Test pattern-based cache invalidation."""
        cache = CacheManager()

        # Add some test data
        cache.set("repo:123", {"name": "repo1"})
        cache.set("repo:456", {"name": "repo2"})
        cache.set("doc:789", {"name": "doc1"})

        # Invalidate repo pattern
        deleted = cache.delete_pattern("repo:")
        assert deleted == 2

        # Verify deletion
        assert cache.get("repo:123") is None
        assert cache.get("repo:456") is None
        assert cache.get("doc:789") is not None


class TestCacheDecorator:
    """Test cache decorator functionality."""

    def setup_method(self):
        """Setup for each test."""
        clear_default_cache()

    def test_cached_decorator_sync(self):
        """Test @cached decorator on sync function."""
        call_count = 0

        class TestAPI:
            @cached(ttl=60)
            def get_data(self, item_id: int):
                nonlocal call_count
                call_count += 1
                return {"id": item_id, "data": "test"}

        api = TestAPI()

        # First call - should call function
        result1 = api.get_data(123)
        assert result1 == {"id": 123, "data": "test"}
        assert call_count == 1

        # Second call - should use cache
        result2 = api.get_data(123)
        assert result2 == {"id": 123, "data": "test"}
        assert call_count == 1  # Not incremented

        # Different param - should call function
        result3 = api.get_data(456)
        assert result3 == {"id": 456, "data": "test"}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cached_decorator_async(self):
        """Test @cached decorator on async function."""
        call_count = 0

        class TestAPI:
            @cached(ttl=60)
            async def get_data_async(self, item_id: int):
                nonlocal call_count
                call_count += 1
                return {"id": item_id, "data": "test"}

        api = TestAPI()

        # First call
        result1 = await api.get_data_async(123)
        assert result1 == {"id": 123, "data": "test"}
        assert call_count == 1

        # Second call - should use cache
        result2 = await api.get_data_async(123)
        assert result2 == {"id": 123, "data": "test"}
        assert call_count == 1

    def test_invalidate_cache_decorator(self):
        """Test @invalidate_cache decorator."""
        from yuque.mcp.cache import get_default_cache

        cache = get_default_cache()
        cache.set("repo:123", {"name": "repo1"})
        cache.set("repo:456", {"name": "repo2"})

        class TestAPI:
            @invalidate_cache("repo:")
            def update_repo(self, repo_id: int):
                return {"success": True}

        api = TestAPI()
        result = api.update_repo(123)

        assert result == {"success": True}
        assert cache.get("repo:123") is None
        assert cache.get("repo:456") is None


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_simple_args(self):
        """Test with simple arguments."""
        key = generate_cache_key(123, "test")
        assert "123" in key
        assert "test" in key

    def test_with_kwargs(self):
        """Test with keyword arguments."""
        key = generate_cache_key(123, name="test", value="data")
        assert "123" in key
        assert "name=test" in key
        assert "value=data" in key

    def test_complex_objects(self):
        """Test with complex objects."""
        key = generate_cache_key({"id": 123, "name": "test"})
        # Should serialize to JSON
        assert key is not None
        assert len(key) > 0

    def test_long_key_hashing(self):
        """Test that long keys are hashed."""
        # Create a very long key
        long_string = "x" * 300
        key = generate_cache_key(long_string)

        # Should be hashed to MD5
        assert len(key) == 32  # MD5 hex length


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
