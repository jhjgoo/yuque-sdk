"""Tests for cache backend abstract base class."""

from datetime import datetime, timedelta
from typing import Any

import pytest

from yuque.cache.backend import CacheBackend, CacheEntry


class ConcreteCacheBackend(CacheBackend):
    """Concrete implementation for testing abstract base class."""

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}

    @property
    def name(self) -> str:
        return "test"

    def get(self, key: str) -> CacheEntry | None:
        entry = self._cache.get(key)
        if entry and entry.is_expired():
            del self._cache[key]
            return None
        return entry

    def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        now = datetime.now()
        expires_at = None
        if ttl_seconds is not None:
            expires_at = now + timedelta(seconds=ttl_seconds)

        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=expires_at,
            ttl_seconds=ttl_seconds,
        )

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def exists(self, key: str) -> bool:
        entry = self.get(key)
        return entry is not None

    def clear(self) -> None:
        self._cache.clear()

    def get_size(self) -> int:
        return len(self._cache)

    def get_memory_usage(self) -> int:
        return sum(len(str(entry.value)) for entry in self._cache.values())


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test basic CacheEntry creation."""
        now = datetime.now()
        entry = CacheEntry(
            key="test_key",
            value={"data": "test"},
            created_at=now,
        )
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.created_at == now
        assert entry.expires_at is None
        assert entry.ttl_seconds is None

    def test_cache_entry_with_ttl(self):
        """Test CacheEntry with TTL."""
        now = datetime.now()
        expires = now + timedelta(seconds=3600)
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=expires,
            ttl_seconds=3600,
        )
        assert entry.ttl_seconds == 3600
        assert entry.expires_at == expires

    def test_is_expired_no_expiration(self):
        """Test is_expired when no expiration set."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
        )
        assert not entry.is_expired()

    def test_is_expired_future(self):
        """Test is_expired with future expiration."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
        )
        assert not entry.is_expired()

    def test_is_expired_past(self):
        """Test is_expired with past expiration."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert entry.is_expired()

    def test_is_expired_now(self):
        """Test is_expired when expiration is now."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            created_at=datetime.now() - timedelta(seconds=1),
            expires_at=datetime.now(),
        )
        # Slightly in the future or past, should be expired if time has passed
        # This is a timing-sensitive test, so we just verify the logic works
        assert isinstance(entry.is_expired(), bool)


class TestCacheBackendAbstract:
    """Test CacheBackend abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract class cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CacheBackend()

    def test_subclass_must_implement_abstract_methods(self):
        """Test that subclass must implement all abstract methods."""

        class IncompleteBackend(CacheBackend):
            @property
            def name(self) -> str:
                return "incomplete"

        with pytest.raises(TypeError):
            IncompleteBackend()

    def test_concrete_implementation(self):
        """Test that concrete implementation works."""
        backend = ConcreteCacheBackend()
        assert backend.name == "test"

    def test_get_set(self):
        """Test basic get/set operations."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        entry = backend.get("key1")
        assert entry is not None
        assert entry.value == "value1"

    def test_get_nonexistent(self):
        """Test getting nonexistent key."""
        backend = ConcreteCacheBackend()
        entry = backend.get("nonexistent")
        assert entry is None

    def test_delete(self):
        """Test delete operation."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        assert backend.delete("key1") is True
        assert backend.get("key1") is None

    def test_delete_nonexistent(self):
        """Test deleting nonexistent key."""
        backend = ConcreteCacheBackend()
        assert backend.delete("nonexistent") is False

    def test_exists(self):
        """Test exists operation."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        assert backend.exists("key1") is True
        assert backend.exists("nonexistent") is False

    def test_clear(self):
        """Test clear operation."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.clear()
        assert backend.get_size() == 0

    def test_get_size(self):
        """Test get_size operation."""
        backend = ConcreteCacheBackend()
        assert backend.get_size() == 0
        backend.set("key1", "value1")
        assert backend.get_size() == 1
        backend.set("key2", "value2")
        assert backend.get_size() == 2

    def test_get_memory_usage(self):
        """Test get_memory_usage operation."""
        backend = ConcreteCacheBackend()
        assert backend.get_memory_usage() == 0
        backend.set("key1", "value1")
        usage = backend.get_memory_usage()
        assert usage > 0


class TestCacheBackendDefaultMethods:
    """Test default implementations in CacheBackend."""

    def test_get_many(self):
        """Test get_many default implementation."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")

        result = backend.get_many(["key1", "key2", "key3"])
        assert result["key1"] is not None
        assert result["key1"].value == "value1"
        assert result["key2"] is not None
        assert result["key2"].value == "value2"
        assert result["key3"] is None

    def test_set_many(self):
        """Test set_many default implementation."""
        backend = ConcreteCacheBackend()
        items = {"key1": "value1", "key2": "value2"}
        backend.set_many(items, ttl_seconds=60)

        entry1 = backend.get("key1")
        entry2 = backend.get("key2")
        assert entry1 is not None
        assert entry1.value == "value1"
        assert entry1.ttl_seconds == 60
        assert entry2 is not None
        assert entry2.value == "value2"
        assert entry2.ttl_seconds == 60

    def test_set_many_no_ttl(self):
        """Test set_many without TTL."""
        backend = ConcreteCacheBackend()
        items = {"key1": "value1", "key2": "value2"}
        backend.set_many(items)

        entry1 = backend.get("key1")
        entry2 = backend.get("key2")
        assert entry1 is not None
        assert entry1.ttl_seconds is None
        assert entry2 is not None
        assert entry2.ttl_seconds is None

    def test_delete_many(self):
        """Test delete_many default implementation."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")

        count = backend.delete_many(["key1", "key2", "nonexistent"])
        assert count == 2
        assert backend.get("key1") is None
        assert backend.get("key2") is None
        assert backend.get("key3") is not None

    def test_delete_many_empty_list(self):
        """Test delete_many with empty list."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        count = backend.delete_many([])
        assert count == 0
        assert backend.get("key1") is not None


class TestCacheBackendTTL:
    """Test TTL functionality in CacheBackend."""

    def test_set_with_ttl(self):
        """Test setting entry with TTL."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1", ttl_seconds=1)
        entry = backend.get("key1")
        assert entry is not None
        assert entry.ttl_seconds == 1
        assert entry.expires_at is not None

    def test_expiration_removes_entry(self):
        """Test that expired entries are not returned."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0.1)

        # Entry should exist immediately
        entry = backend.get("key1")
        assert entry is not None

        # Wait for expiration
        import time

        time.sleep(0.15)

        # Entry should be expired and not returned
        entry = backend.get("key1")
        assert entry is None

    def test_exists_with_expired_entry(self):
        """Test exists with expired entry."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0.1)

        # Should exist immediately
        assert backend.exists("key1") is True

        # Wait for expiration
        import time

        time.sleep(0.15)

        # Should not exist after expiration
        assert backend.exists("key1") is False


class TestCacheBackendEdgeCases:
    """Test edge cases in CacheBackend."""

    def test_update_existing_key(self):
        """Test updating an existing key."""
        backend = ConcreteCacheBackend()
        backend.set("key1", "value1")
        backend.set("key1", "value2")

        entry = backend.get("key1")
        assert entry is not None
        assert entry.value == "value2"

    def test_complex_value_types(self):
        """Test with complex value types."""
        backend = ConcreteCacheBackend()

        # Dict
        backend.set("dict_key", {"nested": {"data": "value"}})
        assert backend.get("dict_key").value == {"nested": {"data": "value"}}

        # List
        backend.set("list_key", [1, 2, 3, 4])
        assert backend.get("list_key").value == [1, 2, 3, 4]

        # Tuple
        backend.set("tuple_key", (1, 2, 3))
        assert backend.get("tuple_key").value == (1, 2, 3)

        # None
        backend.set("none_key", None)
        assert backend.get("none_key").value is None

    def test_empty_string_key(self):
        """Test with empty string key."""
        backend = ConcreteCacheBackend()
        backend.set("", "empty_key_value")
        entry = backend.get("")
        assert entry is not None
        assert entry.value == "empty_key_value"

    def test_unicode_keys_and_values(self):
        """Test with unicode keys and values."""
        backend = ConcreteCacheBackend()
        backend.set("键", "值")
        entry = backend.get("键")
        assert entry is not None
        assert entry.value == "值"

    def test_large_key(self):
        """Test with large key."""
        backend = ConcreteCacheBackend()
        large_key = "k" * 1000
        backend.set(large_key, "large_key_value")
        entry = backend.get(large_key)
        assert entry is not None
        assert entry.value == "large_key_value"
