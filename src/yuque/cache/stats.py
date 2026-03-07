"""Cache statistics tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any


@dataclass
class CacheStats:
    """Cache statistics container."""

    # Counters
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    errors: int = 0

    # Memory tracking
    memory_bytes: int = 0
    entry_count: int = 0

    # Timing
    total_get_time_ms: float = 0.0
    total_set_time_ms: float = 0.0

    # Metadata
    backend_name: str = "unknown"
    created_at: datetime = field(default_factory=datetime.now)
    last_reset_at: datetime | None = None

    @property
    def total_requests(self) -> int:
        """Total number of get requests (hits + misses)."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a percentage (0-100)."""
        if self.total_requests == 0:
            return 0.0
        return (self.hits / self.total_requests) * 100

    @property
    def miss_rate(self) -> float:
        """Cache miss rate as a percentage (0-100)."""
        if self.total_requests == 0:
            return 0.0
        return (self.misses / self.total_requests) * 100

    @property
    def avg_get_time_ms(self) -> float:
        """Average time for get operations in milliseconds."""
        if self.total_requests == 0:
            return 0.0
        return self.total_get_time_ms / self.total_requests

    @property
    def avg_set_time_ms(self) -> float:
        """Average time for set operations in milliseconds."""
        if self.sets == 0:
            return 0.0
        return self.total_set_time_ms / self.sets

    @property
    def memory_mb(self) -> float:
        """Memory usage in megabytes."""
        return self.memory_bytes / (1024 * 1024)

    def to_dict(self) -> dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 2),
            "miss_rate": round(self.miss_rate, 2),
            "sets": self.sets,
            "deletes": self.deletes,
            "evictions": self.evictions,
            "errors": self.errors,
            "memory_bytes": self.memory_bytes,
            "memory_mb": round(self.memory_mb, 2),
            "entry_count": self.entry_count,
            "avg_get_time_ms": round(self.avg_get_time_ms, 4),
            "avg_set_time_ms": round(self.avg_set_time_ms, 4),
            "backend_name": self.backend_name,
            "created_at": self.created_at.isoformat(),
            "last_reset_at": (self.last_reset_at.isoformat() if self.last_reset_at else None),
        }


class StatsTracker:
    """Thread-safe cache statistics tracker."""

    def __init__(self, backend_name: str = "unknown") -> None:
        self._stats = CacheStats(backend_name=backend_name)
        self._lock = Lock()

    def record_hit(self, time_ms: float = 0.0) -> None:
        """Record a cache hit."""
        with self._lock:
            self._stats.hits += 1
            self._stats.total_get_time_ms += time_ms

    def record_miss(self, time_ms: float = 0.0) -> None:
        """Record a cache miss."""
        with self._lock:
            self._stats.misses += 1
            self._stats.total_get_time_ms += time_ms

    def record_set(self, time_ms: float = 0.0) -> None:
        """Record a cache set operation."""
        with self._lock:
            self._stats.sets += 1
            self._stats.total_set_time_ms += time_ms

    def record_delete(self) -> None:
        """Record a cache delete operation."""
        with self._lock:
            self._stats.deletes += 1

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        with self._lock:
            self._stats.evictions += 1

    def record_error(self) -> None:
        """Record a cache error."""
        with self._lock:
            self._stats.errors += 1

    def update_memory(self, bytes_count: int) -> None:
        """Update memory usage."""
        with self._lock:
            self._stats.memory_bytes = bytes_count

    def update_entry_count(self, count: int) -> None:
        """Update entry count."""
        with self._lock:
            self._stats.entry_count = count

    def get_stats(self) -> CacheStats:
        """Get current statistics (returns a copy)."""
        with self._lock:
            # Return a copy to prevent external modification
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                sets=self._stats.sets,
                deletes=self._stats.deletes,
                evictions=self._stats.evictions,
                errors=self._stats.errors,
                memory_bytes=self._stats.memory_bytes,
                entry_count=self._stats.entry_count,
                total_get_time_ms=self._stats.total_get_time_ms,
                total_set_time_ms=self._stats.total_set_time_ms,
                backend_name=self._stats.backend_name,
                created_at=self._stats.created_at,
                last_reset_at=self._stats.last_reset_at,
            )

    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self._stats = CacheStats(backend_name=self._stats.backend_name)
            self._stats.last_reset_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Get stats as dictionary."""
        return self.get_stats().to_dict()
