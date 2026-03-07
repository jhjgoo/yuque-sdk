"""Redis cache backend implementation (optional dependency)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .backend import CacheBackend, CacheEntry

if TYPE_CHECKING:
    import redis.asyncio as aioredis


class RedisCacheBackend(CacheBackend):
    """Redis-based cache backend with async support."""

    def __init__(
        self,
        redis_client: aioredis.Redis | None = None,
        url: str = "redis://localhost:6379/0",
        key_prefix: str = "yuque:",
    ) -> None:
        self._redis: aioredis.Redis | None = redis_client
        self._url = url
        self._key_prefix = key_prefix
        self._owns_client = redis_client is None

    @property
    def name(self) -> str:
        return "redis"

    async def _get_client(self) -> aioredis.Redis:
        """Get or create Redis client."""
        if self._redis is None:
            try:
                import redis.asyncio as aioredis

                self._redis = aioredis.from_url(self._url)
            except ImportError as e:
                raise ImportError(
                    "Redis support requires 'redis' package. "
                    "Install with: pip install yuque-sdk[redis]"
                ) from e
        return self._redis

    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self._key_prefix}{key}"

    def get(self, key: str) -> CacheEntry | None:
        """Synchronous get - not recommended for Redis, use get_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use get_async() instead.")

    async def get_async(self, key: str) -> CacheEntry | None:
        """Get a cache entry asynchronously."""
        client = await self._get_client()
        full_key = self._make_key(key)

        try:
            data = await client.get(full_key)
            if data is None:
                return None

            import json

            cached = json.loads(data)
            return CacheEntry(
                key=key,
                value=cached["value"],
                created_at=datetime.fromisoformat(cached["created_at"]),
                expires_at=(
                    datetime.fromisoformat(cached["expires_at"])
                    if cached.get("expires_at")
                    else None
                ),
                ttl_seconds=cached.get("ttl_seconds"),
            )
        except Exception:
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
    ) -> None:
        """Synchronous set - not recommended for Redis, use set_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use set_async() instead.")

    async def set_async(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
    ) -> None:
        """Set a cache entry asynchronously."""
        client = await self._get_client()
        full_key = self._make_key(key)

        now = datetime.now()
        expires_at = None
        if ttl_seconds is not None:
            expires_at = datetime.fromtimestamp(now.timestamp() + ttl_seconds)

        import json

        data = {
            "value": value,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "ttl_seconds": ttl_seconds,
        }

        if ttl_seconds is not None:
            await client.setex(full_key, int(ttl_seconds), json.dumps(data))
        else:
            await client.set(full_key, json.dumps(data))

    def delete(self, key: str) -> bool:
        """Synchronous delete - not recommended for Redis, use delete_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use delete_async() instead.")

    async def delete_async(self, key: str) -> bool:
        """Delete a cache entry asynchronously."""
        client = await self._get_client()
        full_key = self._make_key(key)

        try:
            result = await client.delete(full_key)
            return result > 0
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        """Synchronous exists - not recommended for Redis, use exists_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use exists_async() instead.")

    async def exists_async(self, key: str) -> bool:
        """Check if key exists asynchronously."""
        client = await self._get_client()
        full_key = self._make_key(key)

        try:
            return bool(await client.exists(full_key))
        except Exception:
            return False

    def clear(self) -> None:
        """Synchronous clear - not recommended for Redis, use clear_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use clear_async() instead.")

    async def clear_async(self) -> None:
        """Clear all cache entries with prefix."""
        client = await self._get_client()

        try:
            keys = await client.keys(f"{self._key_prefix}*")
            if keys:
                await client.delete(*keys)
        except Exception:
            pass

    def get_size(self) -> int:
        """Get size - not supported for Redis, use get_size_async."""
        raise NotImplementedError("RedisCacheBackend requires async. Use get_size_async() instead.")

    async def get_size_async(self) -> int:
        """Get number of cached entries."""
        client = await self._get_client()

        try:
            keys = await client.keys(f"{self._key_prefix}*")
            return len(keys)
        except Exception:
            return 0

    def get_memory_usage(self) -> int:
        """Get memory usage - not supported for Redis."""
        return -1

    async def close(self) -> None:
        """Close Redis connection if we own the client."""
        if self._owns_client and self._redis is not None:
            await self._redis.close()
            self._redis = None
