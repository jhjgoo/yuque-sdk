"""Tests for memory cache backend."""

import time
from datetime import datetime

import pytest

from yuque.cache.backend import CacheEntry
from yuque.cache.memory import MemoryCacheBackend


class TestMemoryCacheBackendInit:
    """Test MemoryCacheBackend initialization."""

    def test_init_default(self):
        backend = MemoryCacheBackend()
        assert backend._max_size == 1000
        assert backend._max_memory_bytes == 100 * 1024 * 1024
        assert backend._current_memory == 0
        assert len(backend._cache) == 0

    def test_init_custom_size(self):
        backend = MemoryCacheBackend(max_size=500)
        assert backend._max_size == 500

    def test_init_custom_memory(self):
        backend = MemoryCacheBackend(max_memory_mb=50.0)
        assert backend._max_memory_bytes == 50 * 1024 * 1024

    def test_init_custom_both(self):
        backend = MemoryCacheBackend(max_size=100, max_memory_mb=10.0)
        assert backend._max_size == 100
        assert backend._max_memory_bytes == 10 * 1024 * 1024

    def test_name_property(self):
        backend = MemoryCacheBackend()
        assert backend.name == "memory"


class TestMemoryCacheBackendGetSet:
    """Test get/set operations."""

    def test_set_and_get(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        entry = backend.get("key1")
        assert entry is not None
        assert entry.value == "value1"
        assert entry.key == "key1"

    def test_set_with_ttl(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=60)
        entry = backend.get("key1")
        assert entry is not None
        assert entry.ttl_seconds == 60
        assert entry.expires_at is not None

    def test_get_nonexistent(self):
        backend = MemoryCacheBackend()
        entry = backend.get("nonexistent")
        assert entry is None

    def test_get_updates_lru(self):
        backend = MemoryCacheBackend(max_size=3)
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")

        backend.get("key1")

        backend.set("key4", "value4")

        assert backend.get("key1") is not None
        assert backend.get("key2") is None
        assert backend.get("key3") is not None
        assert backend.get("key4") is not None

    def test_update_existing_key(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        backend.set("key1", "value2")
        entry = backend.get("key1")
        assert entry.value == "value2"

    def test_complex_values(self):
        backend = MemoryCacheBackend()

        backend.set("dict", {"nested": "value"})
        assert backend.get("dict").value == {"nested": "value"}

        backend.set("list", [1, 2, 3])
        assert backend.get("list").value == [1, 2, 3]

        backend.set("tuple", (1, 2, 3))
        assert backend.get("tuple").value == (1, 2, 3)


class TestMemoryCacheBackendDelete:
    """Test delete operations."""

    def test_delete_existing(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        result = backend.delete("key1")
        assert result is True
        assert backend.get("key1") is None

    def test_delete_nonexistent(self):
        backend = MemoryCacheBackend()
        result = backend.delete("nonexistent")
        assert result is False

    def test_delete_updates_memory(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        initial_memory = backend.get_memory_usage()

        backend.delete("key1")

        assert backend.get_memory_usage() < initial_memory


class TestMemoryCacheBackendExists:
    """Test exists operations."""

    def test_exists_true(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        assert backend.exists("key1") is True

    def test_exists_false(self):
        backend = MemoryCacheBackend()
        assert backend.exists("nonexistent") is False

    def test_exists_after_delete(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        backend.delete("key1")
        assert backend.exists("key1") is False


class TestMemoryCacheBackendClear:
    """Test clear operations."""

    def test_clear_empty(self):
        backend = MemoryCacheBackend()
        backend.clear()
        assert backend.get_size() == 0

    def test_clear_with_entries(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.clear()
        assert backend.get_size() == 0
        assert backend.get_memory_usage() == 0

    def test_clear_resets_memory(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        assert backend.get_memory_usage() > 0

        backend.clear()
        assert backend.get_memory_usage() == 0


class TestMemoryCacheBackendSize:
    """Test size operations."""

    def test_get_size_empty(self):
        backend = MemoryCacheBackend()
        assert backend.get_size() == 0

    def test_get_size_with_entries(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        assert backend.get_size() == 1

        backend.set("key2", "value2")
        assert backend.get_size() == 2

    def test_get_size_after_delete(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.delete("key1")
        assert backend.get_size() == 1


class TestMemoryCacheBackendMemory:
    """Test memory usage operations."""

    def test_get_memory_usage_empty(self):
        backend = MemoryCacheBackend()
        assert backend.get_memory_usage() == 0

    def test_get_memory_usage_with_entries(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")
        assert backend.get_memory_usage() > 0

        backend.set("key2", "value2")
        assert backend.get_memory_usage() > 0

    def test_memory_increases_with_value_size(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "small")
        small_memory = backend.get_memory_usage()

        backend.set("key2", "x" * 1000)
        large_memory = backend.get_memory_usage()

        assert large_memory > small_memory


class TestMemoryCacheBackendTTL:
    """Test TTL expiration."""

    def test_ttl_not_expired(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=60)
        entry = backend.get("key1")
        assert entry is not None

    def test_ttl_expired(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0.1)

        time.sleep(0.15)

        entry = backend.get("key1")
        assert entry is None

    def test_ttl_expired_deleted_from_cache(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0.1)

        assert backend.get_size() == 1

        time.sleep(0.15)

        backend.get("key1")

        assert backend.get_size() == 0

    def test_no_ttl_no_expiration(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1")

        time.sleep(0.1)

        entry = backend.get("key1")
        assert entry is not None

    def test_exists_with_expired_entry(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0.1)

        assert backend.exists("key1") is True

        time.sleep(0.15)

        assert backend.exists("key1") is False


class TestMemoryCacheBackendLRU:
    """Test LRU eviction."""

    def test_lru_eviction_on_max_size(self):
        backend = MemoryCacheBackend(max_size=3)
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")
        backend.set("key4", "value4")

        assert backend.get("key1") is None
        assert backend.get("key2") is not None
        assert backend.get("key3") is not None
        assert backend.get("key4") is not None

    def test_lru_updates_on_get(self):
        backend = MemoryCacheBackend(max_size=3)
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")

        backend.get("key1")

        backend.set("key4", "value4")

        assert backend.get("key1") is not None
        assert backend.get("key2") is None
        assert backend.get("key3") is not None
        assert backend.get("key4") is not None

    def test_lru_multiple_evictions(self):
        backend = MemoryCacheBackend(max_size=2)
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "value3")
        backend.set("key4", "value4")

        assert backend.get_size() == 2
        assert backend.get("key1") is None
        assert backend.get("key2") is None
        assert backend.get("key3") is not None
        assert backend.get("key4") is not None


class TestMemoryCacheBackendMemoryEviction:
    """Test memory-based eviction."""

    def test_memory_eviction(self):
        backend = MemoryCacheBackend(max_memory_mb=0.0001)

        for i in range(100):
            backend.set(f"key{i}", "x" * 100)

        assert backend.get_memory_usage() <= backend._max_memory_bytes

    def test_memory_eviction_order(self):
        backend = MemoryCacheBackend(max_memory_mb=0.001)
        backend.set("key1", "value1")
        backend.set("key2", "value2")
        backend.set("key3", "x" * 10000)

        assert backend.get("key1") is None
        assert backend.get("key2") is None


class TestMemoryCacheBackendThreadSafety:
    """Test thread safety."""

    def test_concurrent_access(self):
        import threading

        backend = MemoryCacheBackend()
        errors = []

        def writer(start, count):
            try:
                for i in range(start, start + count):
                    backend.set(f"key{i}", f"value{i}")
            except Exception as e:
                errors.append(e)

        def reader(start, count):
            try:
                for i in range(start, start + count):
                    backend.get(f"key{i}")
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=writer, args=(0, 100)),
            threading.Thread(target=writer, args=(100, 100)),
            threading.Thread(target=reader, args=(0, 100)),
            threading.Thread(target=reader, args=(100, 100)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestMemoryCacheBackendInternalMethods:
    """Test internal methods."""

    def test_estimate_size_string(self):
        backend = MemoryCacheBackend()
        size = backend._estimate_size("test")
        assert size > 0

    def test_estimate_size_dict(self):
        backend = MemoryCacheBackend()
        size = backend._estimate_size({"key": "value"})
        assert size > 0

    def test_estimate_size_list(self):
        backend = MemoryCacheBackend()
        size = backend._estimate_size([1, 2, 3])
        assert size > 0

    def test_timestamp_to_datetime(self):
        timestamp = time.time()
        dt = MemoryCacheBackend._timestamp_to_datetime(timestamp)
        assert isinstance(dt, datetime)
        assert abs(dt.timestamp() - timestamp) < 1.0


class TestMemoryCacheBackendEdgeCases:
    """Test edge cases."""

    def test_empty_key(self):
        backend = MemoryCacheBackend()
        backend.set("", "empty_key_value")
        entry = backend.get("")
        assert entry is not None
        assert entry.value == "empty_key_value"

    def test_unicode_keys_and_values(self):
        backend = MemoryCacheBackend()
        backend.set("键", "值")
        entry = backend.get("键")
        assert entry is not None
        assert entry.value == "值"

    def test_large_key(self):
        backend = MemoryCacheBackend()
        large_key = "k" * 1000
        backend.set(large_key, "large_key_value")
        entry = backend.get(large_key)
        assert entry is not None
        assert entry.value == "large_key_value"

    def test_none_value(self):
        backend = MemoryCacheBackend()
        backend.set("key1", None)
        entry = backend.get("key1")
        assert entry is not None
        assert entry.value is None

    def test_zero_ttl(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=0)
        entry = backend.get("key1")
        assert entry is None

    def test_negative_ttl(self):
        backend = MemoryCacheBackend()
        backend.set("key1", "value1", ttl_seconds=-1)
        entry = backend.get("key1")
        assert entry is None

    def test_very_small_max_size(self):
        backend = MemoryCacheBackend(max_size=1)
        backend.set("key1", "value1")
        backend.set("key2", "value2")

        assert backend.get_size() == 1
        assert backend.get("key1") is None
        assert backend.get("key2") is not None

    def test_zero_max_size(self):
        backend = MemoryCacheBackend(max_size=0)
        backend.set("key1", "value1")

        assert backend.get_size() == 0
