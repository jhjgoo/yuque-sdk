"""Cache backend abstract base class and protocols."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class CacheEntry:
    """Represents a cached entry with metadata."""

    key: str
    value: Any
    created_at: datetime
    expires_at: datetime | None = None
    ttl_seconds: float | None = None

    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class CacheBackend(ABC):
    """
    Abstract base class for cache backends.

    All cache backends must implement this interface to be used
    with the CacheManager.
    """

    @abstractmethod
    def get(self, key: str) -> CacheEntry | None:
        """
        Get a cache entry by key.

        Args:
            key: The cache key.

        Returns:
            CacheEntry if found and not expired, None otherwise.
        """
        ...

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
    ) -> None:
        """
        Set a cache entry.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl_seconds: Time to live in seconds. None means no expiration.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: The cache key.

        Returns:
            True if the entry was deleted, False if it didn't exist.
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a cache entry exists and is not expired.

        Args:
            key: The cache key.

        Returns:
            True if the entry exists and is not expired.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    @abstractmethod
    def get_size(self) -> int:
        """
        Get the number of entries in the cache.

        Returns:
            Number of cache entries.
        """
        ...

    @abstractmethod
    def get_memory_usage(self) -> int:
        """
        Get approximate memory usage in bytes.

        Returns:
            Memory usage in bytes.
        """
        ...

    def get_many(self, keys: list[str]) -> dict[str, CacheEntry | None]:
        """
        Get multiple cache entries.

        Args:
            keys: List of cache keys.

        Returns:
            Dictionary mapping keys to CacheEntry or None.
        """
        return {key: self.get(key) for key in keys}

    def set_many(
        self,
        items: dict[str, Any],
        ttl_seconds: float | None = None,
    ) -> None:
        """
        Set multiple cache entries.

        Args:
            items: Dictionary of key-value pairs to cache.
            ttl_seconds: Time to live in seconds for all entries.
        """
        for key, value in items.items():
            self.set(key, value, ttl_seconds)

    def delete_many(self, keys: list[str]) -> int:
        """
        Delete multiple cache entries.

        Args:
            keys: List of cache keys.

        Returns:
            Number of entries deleted.
        """
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the backend name for logging/debugging."""
        ...
