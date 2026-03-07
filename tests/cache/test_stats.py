"""Tests for cache statistics tracking."""

from __future__ import annotations

import threading
import time
from datetime import datetime

import pytest

from yuque.cache.stats import CacheStats, StatsTracker


class TestCacheStatsDefaults:
    """Tests for CacheStats default values."""

    def test_cache_stats_default_values(self) -> None:
        """Initial state has zero values."""
        stats = CacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0
        assert stats.deletes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        assert stats.memory_bytes == 0
        assert stats.entry_count == 0
        assert stats.total_get_time_ms == 0.0
        assert stats.total_set_time_ms == 0.0
        assert stats.backend_name == "unknown"
        assert isinstance(stats.created_at, datetime)
        assert stats.last_reset_at is None

    def test_cache_stats_custom_backend_name(self) -> None:
        """Backend name can be customized."""
        stats = CacheStats(backend_name="redis")

        assert stats.backend_name == "redis"


class TestCacheStatsProperties:
    """Tests for CacheStats computed properties."""

    def test_total_requests(self) -> None:
        """Total requests is hits + misses."""
        stats = CacheStats(hits=10, misses=5)

        assert stats.total_requests == 15

    def test_total_requests_zero(self) -> None:
        """Total requests is 0 when no activity."""
        stats = CacheStats()

        assert stats.total_requests == 0

    def test_hit_rate_calculation(self) -> None:
        """hit_rate property calculates correctly."""
        stats = CacheStats(hits=75, misses=25)

        assert stats.hit_rate == 75.0

    def test_hit_rate_with_zero_requests(self) -> None:
        """Division by zero returns 0.0."""
        stats = CacheStats()

        assert stats.hit_rate == 0.0

    def test_miss_rate_calculation(self) -> None:
        """miss_rate property calculates correctly."""
        stats = CacheStats(hits=75, misses=25)

        assert stats.miss_rate == 25.0

    def test_miss_rate_with_zero_requests(self) -> None:
        """Division by zero returns 0.0."""
        stats = CacheStats()

        assert stats.miss_rate == 0.0

    def test_avg_get_time_calculation(self) -> None:
        """Average time for get operations."""
        stats = CacheStats(hits=5, misses=5, total_get_time_ms=100.0)

        assert stats.avg_get_time_ms == 10.0

    def test_avg_get_time_zero_requests(self) -> None:
        """Average get time is 0 with no requests."""
        stats = CacheStats()

        assert stats.avg_get_time_ms == 0.0

    def test_avg_set_time_calculation(self) -> None:
        """Average time for set operations."""
        stats = CacheStats(sets=10, total_set_time_ms=50.0)

        assert stats.avg_set_time_ms == 5.0

    def test_avg_set_time_zero_sets(self) -> None:
        """Average set time is 0 with no sets."""
        stats = CacheStats()

        assert stats.avg_set_time_ms == 0.0

    def test_memory_mb_conversion(self) -> None:
        """Memory in MB."""
        stats = CacheStats(memory_bytes=10 * 1024 * 1024)  # 10 MB

        assert stats.memory_mb == 10.0

    def test_memory_mb_zero(self) -> None:
        """Memory is 0 MB when empty."""
        stats = CacheStats()

        assert stats.memory_mb == 0.0


class TestCacheStatsSerialization:
    """Tests for CacheStats serialization."""

    def test_to_dict_serialization(self) -> None:
        """Convert to dictionary."""
        stats = CacheStats(
            hits=100,
            misses=50,
            sets=30,
            deletes=10,
            evictions=5,
            errors=2,
            memory_bytes=1024 * 1024,
            entry_count=100,
            total_get_time_ms=500.0,
            total_set_time_ms=200.0,
            backend_name="test",
        )

        result = stats.to_dict()

        assert result["hits"] == 100
        assert result["misses"] == 50
        assert result["hit_rate"] == 66.67
        assert result["miss_rate"] == 33.33
        assert result["sets"] == 30
        assert result["deletes"] == 10
        assert result["evictions"] == 5
        assert result["errors"] == 2
        assert result["memory_bytes"] == 1024 * 1024
        assert result["memory_mb"] == 1.0
        assert result["entry_count"] == 100
        assert result["backend_name"] == "test"
        assert "created_at" in result
        assert result["last_reset_at"] is None

    def test_to_dict_includes_reset_time(self) -> None:
        """to_dict includes last_reset_at when set."""
        reset_time = datetime.now()
        stats = CacheStats(last_reset_at=reset_time)

        result = stats.to_dict()

        assert result["last_reset_at"] == reset_time.isoformat()


class TestStatsTrackerRecording:
    """Tests for StatsTracker recording methods."""

    def test_record_hit(self) -> None:
        """Increment hit counter."""
        tracker = StatsTracker()
        tracker.record_hit(time_ms=5.0)

        stats = tracker.get_stats()
        assert stats.hits == 1
        assert stats.total_get_time_ms == 5.0

    def test_record_hit_multiple(self) -> None:
        """Multiple hits increment correctly."""
        tracker = StatsTracker()
        tracker.record_hit()
        tracker.record_hit()
        tracker.record_hit()

        stats = tracker.get_stats()
        assert stats.hits == 3

    def test_record_miss(self) -> None:
        """Increment miss counter."""
        tracker = StatsTracker()
        tracker.record_miss(time_ms=10.0)

        stats = tracker.get_stats()
        assert stats.misses == 1
        assert stats.total_get_time_ms == 10.0

    def test_record_miss_multiple(self) -> None:
        """Multiple misses increment correctly."""
        tracker = StatsTracker()
        tracker.record_miss()
        tracker.record_miss()

        stats = tracker.get_stats()
        assert stats.misses == 2

    def test_record_set(self) -> None:
        """Increment set counter."""
        tracker = StatsTracker()
        tracker.record_set(time_ms=3.0)

        stats = tracker.get_stats()
        assert stats.sets == 1
        assert stats.total_set_time_ms == 3.0

    def test_record_set_multiple(self) -> None:
        """Multiple sets increment correctly."""
        tracker = StatsTracker()
        tracker.record_set()
        tracker.record_set()
        tracker.record_set()

        stats = tracker.get_stats()
        assert stats.sets == 3

    def test_record_delete(self) -> None:
        """Increment delete counter."""
        tracker = StatsTracker()
        tracker.record_delete()

        stats = tracker.get_stats()
        assert stats.deletes == 1

    def test_record_eviction(self) -> None:
        """Increment eviction counter."""
        tracker = StatsTracker()
        tracker.record_eviction()

        stats = tracker.get_stats()
        assert stats.evictions == 1

    def test_record_error(self) -> None:
        """Increment error counter."""
        tracker = StatsTracker()
        tracker.record_error()

        stats = tracker.get_stats()
        assert stats.errors == 1


class TestStatsTrackerUpdates:
    """Tests for StatsTracker update methods."""

    def test_update_memory(self) -> None:
        """Update memory usage."""
        tracker = StatsTracker()
        tracker.update_memory(1024 * 512)

        stats = tracker.get_stats()
        assert stats.memory_bytes == 1024 * 512

    def test_update_memory_overwrites(self) -> None:
        """Update memory overwrites previous value."""
        tracker = StatsTracker()
        tracker.update_memory(1000)
        tracker.update_memory(2000)

        stats = tracker.get_stats()
        assert stats.memory_bytes == 2000

    def test_update_entry_count(self) -> None:
        """Update count."""
        tracker = StatsTracker()
        tracker.update_entry_count(50)

        stats = tracker.get_stats()
        assert stats.entry_count == 50

    def test_update_entry_count_overwrites(self) -> None:
        """Update entry count overwrites previous value."""
        tracker = StatsTracker()
        tracker.update_entry_count(10)
        tracker.update_entry_count(20)

        stats = tracker.get_stats()
        assert stats.entry_count == 20


class TestStatsTrackerGetStats:
    """Tests for StatsTracker.get_stats method."""

    def test_get_stats_returns_copy(self) -> None:
        """Returns copy, not reference."""
        tracker = StatsTracker()
        tracker.record_hit()

        stats1 = tracker.get_stats()
        tracker.record_hit()
        stats2 = tracker.get_stats()

        assert stats1.hits == 1
        assert stats2.hits == 2

    def test_get_stats_cannot_modify_internal(self) -> None:
        """Modifying returned stats doesn't affect tracker."""
        tracker = StatsTracker()
        tracker.record_hit()

        stats = tracker.get_stats()
        stats.hits = 999  # Modify the copy

        fresh_stats = tracker.get_stats()
        assert fresh_stats.hits == 1


class TestStatsTrackerReset:
    """Tests for StatsTracker.reset method."""

    def test_reset_clears_all_stats(self) -> None:
        """Reset to initial state."""
        tracker = StatsTracker(backend_name="test")
        tracker.record_hit()
        tracker.record_miss()
        tracker.record_set()
        tracker.record_delete()
        tracker.record_eviction()
        tracker.record_error()
        tracker.update_memory(1000)
        tracker.update_entry_count(10)

        tracker.reset()

        stats = tracker.get_stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0
        assert stats.deletes == 0
        assert stats.evictions == 0
        assert stats.errors == 0
        assert stats.memory_bytes == 0
        assert stats.entry_count == 0
        assert stats.total_get_time_ms == 0.0
        assert stats.total_set_time_ms == 0.0
        assert stats.backend_name == "test"
        assert stats.last_reset_at is not None

    def test_reset_preserves_backend_name(self) -> None:
        """Backend name is preserved after reset."""
        tracker = StatsTracker(backend_name="redis")
        tracker.record_hit()

        tracker.reset()

        stats = tracker.get_stats()
        assert stats.backend_name == "redis"


class TestStatsTrackerToDict:
    """Tests for StatsTracker.to_dict method."""

    def test_to_dict(self) -> None:
        """to_dict returns stats dictionary."""
        tracker = StatsTracker(backend_name="memory")
        tracker.record_hit()
        tracker.record_miss()

        result = tracker.to_dict()

        assert result["hits"] == 1
        assert result["misses"] == 1
        assert result["backend_name"] == "memory"


class TestStatsTrackerThreadSafety:
    """Tests for StatsTracker thread safety."""

    def test_thread_safety_concurrent_hits(self) -> None:
        """Thread-safe operations with concurrent hits."""
        tracker = StatsTracker()
        num_threads = 10
        hits_per_thread = 100

        def record_hits() -> None:
            for _ in range(hits_per_thread):
                tracker.record_hit()

        threads = [threading.Thread(target=record_hits) for _ in range(num_threads)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = tracker.get_stats()
        assert stats.hits == num_threads * hits_per_thread

    def test_thread_safety_concurrent_mixed_operations(self) -> None:
        """Thread-safe operations with mixed operations."""
        tracker = StatsTracker()
        num_threads = 5

        def record_mixed(thread_id: int) -> None:
            for i in range(100):
                if i % 4 == 0:
                    tracker.record_hit()
                elif i % 4 == 1:
                    tracker.record_miss()
                elif i % 4 == 2:
                    tracker.record_set()
                else:
                    tracker.record_delete()

        threads = [threading.Thread(target=record_mixed, args=(i,)) for i in range(num_threads)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = tracker.get_stats()
        assert stats.hits == num_threads * 25
        assert stats.misses == num_threads * 25
        assert stats.sets == num_threads * 25
        assert stats.deletes == num_threads * 25

    def test_thread_safety_get_stats_during_writes(self) -> None:
        """get_stats is safe during concurrent writes."""
        tracker = StatsTracker()
        results = []
        stop_flag = threading.Event()

        def writer() -> None:
            while not stop_flag.is_set():
                tracker.record_hit()

        def reader() -> None:
            for _ in range(50):
                stats = tracker.get_stats()
                results.append(stats.hits)
                time.sleep(0.001)

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()

        reader_thread.join()
        stop_flag.set()
        writer_thread.join()

        # All reads should have valid values
        assert all(isinstance(r, int) for r in results)


class TestStatsTrackerInitialization:
    """Tests for StatsTracker initialization."""

    def test_init_default_backend_name(self) -> None:
        """Default backend name is 'unknown'."""
        tracker = StatsTracker()

        stats = tracker.get_stats()
        assert stats.backend_name == "unknown"

    def test_init_custom_backend_name(self) -> None:
        """Custom backend name is stored."""
        tracker = StatsTracker(backend_name="redis")

        stats = tracker.get_stats()
        assert stats.backend_name == "redis"
