"""MCP cache layer with invalidation support.

Wraps SDK CacheManager with MCP-specific features:
- Direct key access (backward compatibility)
- Pattern-based invalidation
- Decorator for automatic cache invalidation
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from yuque.cache import AsyncCacheManager
from yuque.cache import CacheManager as SDKCacheManager

DEFAULT_TTL_CONFIG: dict[str, int] = {
    "/user": 24 * 60 * 60,
    "/repos/": 12 * 60 * 60,
    "/docs?": 6 * 60 * 60,
    "/docs/": 3 * 60 * 60,
    "/search": 1 * 60 * 60,
    "default": 5 * 60,
}


class CacheStats:
    """Cache statistics wrapper for backward compatibility."""

    def __init__(self, stats_dict: dict[str, Any]) -> None:
        self._stats = stats_dict

    @property
    def hits(self) -> int:
        return int(self._stats.get("hits", 0))

    @property
    def misses(self) -> int:
        return int(self._stats.get("misses", 0))

    @property
    def evictions(self) -> int:
        return int(self._stats.get("evictions", 0))

    @property
    def expired(self) -> int:
        return int(self._stats.get("expired", 0))

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expired": self.expired,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "miss_rate": round(self.miss_rate, 4),
        }


class CacheManager:
    """MCP cache manager wrapping SDK cache with invalidation support."""

    def __init__(
        self,
        memory_max_size: int = 1000,
        redis_url: str | None = None,
        ttl_config: dict[str, int] | None = None,
        default_ttl: int = 300,
    ) -> None:
        from yuque.cache import MemoryCacheBackend

        backend = MemoryCacheBackend(max_size=memory_max_size)
        self._sdk_cache = SDKCacheManager(
            backend=backend,
            default_ttl=default_ttl,
        )
        self._ttl_config = {**DEFAULT_TTL_CONFIG, **(ttl_config or {})}
        self._key_to_endpoint: dict[str, str] = {}
        self._async_cache: AsyncCacheManager | None = None
        self._wrapped_keys: set[str] = set()

    def get_ttl_for_endpoint(self, endpoint: str) -> int:
        endpoint_lower = endpoint.lower()

        if endpoint_lower.startswith("/user"):
            return self._ttl_config.get("/user", DEFAULT_TTL_CONFIG["/user"])

        if "/repos/" in endpoint_lower:
            return self._ttl_config.get("/repos/", DEFAULT_TTL_CONFIG["/repos/"])

        if "/search" in endpoint_lower:
            return self._ttl_config.get("/search", DEFAULT_TTL_CONFIG["/search"])

        if "/docs?" in endpoint_lower or (
            "/docs" in endpoint_lower
            and not any(x in endpoint_lower for x in ["/docs/", "/docs\\"])
        ):
            return self._ttl_config.get("/docs?", DEFAULT_TTL_CONFIG["/docs?"])

        if "/docs/" in endpoint_lower:
            return self._ttl_config.get("/docs/", DEFAULT_TTL_CONFIG["/docs/"])

        return self._ttl_config.get("default", DEFAULT_TTL_CONFIG["default"])

    @staticmethod
    def generate_cache_key(
        endpoint: str,
        params: dict[str, Any] | None = None,
        prefix: str = "yuque",
    ) -> str:
        parts = [prefix, endpoint]

        if params:
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            parts.append(param_str)

        key_base = ":".join(parts)

        if len(key_base) > 200:
            import hashlib

            hash_suffix = hashlib.md5(key_base.encode()).hexdigest()[:16]
            return f"{prefix}:{endpoint}:{hash_suffix}"

        return key_base

    def get(self, key: str) -> Any | None:
        endpoint = self._key_to_endpoint.get(key, key)
        result = self._sdk_cache.get(endpoint)
        if key in self._wrapped_keys and isinstance(result, dict) and "data" in result:
            return result["data"]
        return result

    async def get_async(self, key: str) -> Any | None:
        endpoint = self._key_to_endpoint.get(key, key)
        result = await self._get_async_cache().get(endpoint)
        if key in self._wrapped_keys and isinstance(result, dict) and "data" in result:
            return result["data"]
        return result

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        if isinstance(value, dict):
            self._sdk_cache.set(key, value, ttl=ttl)
            self._wrapped_keys.discard(key)
        else:
            self._sdk_cache.set(key, {"data": value}, ttl=ttl)
            self._wrapped_keys.add(key)
        self._key_to_endpoint[key] = key

    async def set_async(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        if isinstance(value, dict):
            await self._get_async_cache().set(key, value, ttl=ttl)
            self._wrapped_keys.discard(key)
        else:
            await self._get_async_cache().set(key, {"data": value}, ttl=ttl)
            self._wrapped_keys.add(key)
        self._key_to_endpoint[key] = key

    def delete(self, key: str) -> bool:
        endpoint = self._key_to_endpoint.get(key, key)
        result = self._sdk_cache.delete(endpoint)
        if result and key in self._key_to_endpoint:
            del self._key_to_endpoint[key]
            self._wrapped_keys.discard(key)
        return result

    async def delete_async(self, key: str) -> bool:
        endpoint = self._key_to_endpoint.get(key, key)
        result = await self._get_async_cache().delete(endpoint)
        if result and key in self._key_to_endpoint:
            del self._key_to_endpoint[key]
            self._wrapped_keys.discard(key)
        return result

    def delete_pattern(self, pattern: str) -> int:
        deleted_count = 0
        keys_to_delete = [key for key in self._key_to_endpoint if pattern in key]

        for key in keys_to_delete:
            if self.delete(key):
                deleted_count += 1

        return deleted_count

    async def delete_pattern_async(self, pattern: str) -> int:
        deleted_count = 0
        keys_to_delete = [key for key in self._key_to_endpoint if pattern in key]

        for key in keys_to_delete:
            if await self.delete_async(key):
                deleted_count += 1

        return deleted_count

    def clear(self) -> None:
        self._sdk_cache.clear()
        self._key_to_endpoint.clear()
        self._wrapped_keys.clear()

    async def clear_async(self) -> None:
        await self._get_async_cache().clear()
        self._key_to_endpoint.clear()
        self._wrapped_keys.clear()

    def get_stats(self) -> dict[str, Any]:
        stats_dict = self._sdk_cache.get_stats_dict()
        stats_dict["size"] = len(self._key_to_endpoint)
        stats_dict["ttl_config"] = self._ttl_config
        return stats_dict

    def cleanup_expired(self) -> int:
        return 0

    @property
    def size(self) -> int:
        return len(self._key_to_endpoint)

    def _get_async_cache(self) -> AsyncCacheManager:
        if self._async_cache is None:
            self._async_cache = AsyncCacheManager(
                backend=self._sdk_cache.backend,
                ttl_policies=self._ttl_config,
            )
        return self._async_cache


def invalidate_cache(*patterns: str) -> Callable:
    """Decorator to invalidate cache after function execution.

    Args:
        patterns: Cache key patterns to invalidate.

    Example:
        @invalidate_cache("/docs/", "/repos/")
        async def update_document(doc_id: int, content: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)
            cache = get_default_cache()
            for pattern in patterns:
                await cache.delete_pattern_async(pattern)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            cache = get_default_cache()
            for pattern in patterns:
                cache.delete_pattern(pattern)
            return result

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def cached(ttl: int | None = None, key_prefix: str = "") -> Callable:
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds. None for default TTL.
        key_prefix: Optional prefix for cache keys.

    Example:
        @cached(ttl=60)
        def get_data(item_id: int):
            return fetch_data(item_id)

        @cached(ttl=300, key_prefix="user")
        async def get_user(user_id: int):
            return await fetch_user(user_id)
    """
    import hashlib

    def decorator(func: Callable) -> Callable:
        def _make_cache_key(*args: Any, **kwargs: Any) -> str:
            # Create a key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            # Add args (skip self/cls for methods)
            start_idx = 1 if args and hasattr(args[0], func.__name__) else 0
            for arg in args[start_idx:]:
                try:
                    key_parts.append(str(arg))
                except Exception:
                    pass

            # Add kwargs
            for k, v in sorted(kwargs.items()):
                try:
                    key_parts.append(f"{k}={v}")
                except Exception:
                    pass

            key = ":".join(key_parts)

            # Hash if too long
            if len(key) > 200:
                key_hash = hashlib.md5(key.encode()).hexdigest()
                key = f"{key_prefix}:{func.__name__}:{key_hash}"

            return key

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_default_cache()
            cache_key = _make_cache_key(*args, **kwargs)

            cached_result = await cache.get_async(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_default_cache()
            cache_key = _make_cache_key(*args, **kwargs)

            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from arguments.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        A cache key string.

    Example:
        key = generate_cache_key(123, "test", name="value")
    """
    import hashlib
    import json

    key_parts = []

    # Add positional args
    for arg in args:
        try:
            if isinstance(arg, dict):
                key_parts.append(
                    hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest()[:16]
                )
            elif isinstance(arg, (list, tuple)):
                key_parts.append(hashlib.md5(json.dumps(arg).encode()).hexdigest()[:16])
            else:
                key_parts.append(str(arg))
        except Exception:
            key_parts.append(str(id(arg)))

    # Add keyword args
    for k, v in sorted(kwargs.items()):
        try:
            if isinstance(v, dict):
                val_str = hashlib.md5(json.dumps(v, sort_keys=True).encode()).hexdigest()[:16]
            elif isinstance(v, (list, tuple)):
                val_str = hashlib.md5(json.dumps(v).encode()).hexdigest()[:16]
            else:
                val_str = str(v)
            key_parts.append(f"{k}={val_str}")
        except Exception:
            key_parts.append(f"{k}={id(v)}")

    key = ":".join(key_parts)

    # Hash if too long (MD5 hex is 32 chars)
    if len(key) > 200:
        return hashlib.md5(key.encode()).hexdigest()

    return key


_default_cache: CacheManager | None = None


def get_default_cache() -> CacheManager:
    global _default_cache
    if _default_cache is None:
        _default_cache = CacheManager()
    return _default_cache


def clear_default_cache() -> None:
    global _default_cache
    if _default_cache is not None:
        _default_cache.clear()
    _default_cache = None


class MemoryCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300) -> None:
        self._manager = CacheManager(
            memory_max_size=max_size,
            default_ttl=default_ttl,
        )

    def get(self, key: str) -> Any | None:
        return self._manager.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._manager.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        return self._manager.delete(key)

    def has(self, key: str) -> bool:
        return self._manager.get(key) is not None

    def clear(self) -> None:
        self._manager.clear()

    def get_stats(self) -> dict[str, Any]:
        return self._manager.get_stats()

    @property
    def size(self) -> int:
        return self._manager.size


MCPCache = MemoryCache


__all__ = [
    "CacheManager",
    "CacheStats",
    "MemoryCache",
    "MCPCache",
    "get_default_cache",
    "clear_default_cache",
    "invalidate_cache",
    "cached",
    "generate_cache_key",
    "DEFAULT_TTL_CONFIG",
]
