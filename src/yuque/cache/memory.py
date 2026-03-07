"""In-memory cache backend implementation."""

from __future__ import annotations

import sys
import time
from collections import OrderedDict
from threading import RLock
from typing import Any

from .backend import CacheBackend, CacheEntry


class MemoryCacheBackend(CacheBackend):
    """Thread-safe in-memory cache backend with LRU eviction."""

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: float = 100.0,
    ) -> None:
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = RLock()
        self._max_size = max_size
        self._max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self._current_memory = 0

    @property
    def name(self) -> str:
        return "memory"

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                self._delete_internal(key)
                return None

            self._cache.move_to_end(key)
            return entry

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
    ) -> None:
        with self._lock:
            now = time.time()
            created_at = type(self)._timestamp_to_datetime(now)

            expires_at = None
            if ttl_seconds is not None:
                expires_at = type(self)._timestamp_to_datetime(now + ttl_seconds)

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=created_at,
                expires_at=expires_at,
                ttl_seconds=ttl_seconds,
            )

            if key in self._cache:
                self._delete_internal(key)

            self._cache[key] = entry
            self._current_memory += self._estimate_size(value)

            self._evict_if_needed()

    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self._cache:
                return False
            self._delete_internal(key)
            return True

    def exists(self, key: str) -> bool:
        entry = self.get(key)
        return entry is not None

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._current_memory = 0

    def get_size(self) -> int:
        with self._lock:
            return len(self._cache)

    def get_memory_usage(self) -> int:
        with self._lock:
            return self._current_memory

    def _delete_internal(self, key: str) -> None:
        """Delete without acquiring lock (must be called with lock held)."""
        entry = self._cache.pop(key, None)
        if entry is not None:
            self._current_memory -= self._estimate_size(entry.value)
            self._current_memory = max(0, self._current_memory)

    def _evict_if_needed(self) -> None:
        """Evict entries if limits exceeded (must be called with lock held)."""
        while len(self._cache) > self._max_size:
            self._evict_oldest()

        while self._current_memory > self._max_memory_bytes and self._cache:
            self._evict_oldest()

    def _evict_oldest(self) -> None:
        """Evict the oldest (least recently used) entry."""
        if not self._cache:
            return
        oldest_key = next(iter(self._cache))
        self._delete_internal(oldest_key)

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value in bytes."""
        try:
            return sys.getsizeof(value)
        except Exception:
            return 1024

    @staticmethod
    def _timestamp_to_datetime(timestamp: float):
        """Convert timestamp to datetime."""
        from datetime import datetime

        return datetime.fromtimestamp(timestamp)
