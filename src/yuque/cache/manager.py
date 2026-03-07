"""Cache manager with TTL policies and graceful degradation."""

from __future__ import annotations

import time
from typing import Any

from .backend import CacheBackend
from .keys import generate_cache_key, get_endpoint_pattern
from .memory import MemoryCacheBackend
from .stats import CacheStats, StatsTracker

TTL_POLICIES: dict[str, float] = {
    "/user": 24 * 60 * 60,  # 24 hours
    "/repos": 12 * 60 * 60,  # 12 hours
    "/repos/*/docs": 6 * 60 * 60,  # 6 hours (doc lists)
    "/docs/": 3 * 60 * 60,  # 3 hours (individual docs)
    "/search": 1 * 60 * 60,  # 1 hour
    "/groups": 12 * 60 * 60,  # 12 hours
}

DEFAULT_TTL = 60 * 60  # 1 hour


class CacheManager:
    """Unified cache manager with TTL policies and statistics."""

    def __init__(
        self,
        backend: CacheBackend | None = None,
        ttl_policies: dict[str, float] | None = None,
        default_ttl: float = DEFAULT_TTL,
        enabled: bool = True,
    ) -> None:
        self._backend = backend or MemoryCacheBackend()
        self._ttl_policies = {**TTL_POLICIES, **(ttl_policies or {})}
        self._default_ttl = default_ttl
        self._enabled = enabled
        self._stats = StatsTracker(backend_name=self._backend.name)

    @property
    def backend(self) -> CacheBackend:
        return self._backend

    @property
    def stats(self) -> CacheStats:
        return self._stats.get_stats()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def get_ttl_for_endpoint(self, endpoint: str) -> float:
        pattern = get_endpoint_pattern(endpoint)
        return self._ttl_policies.get(pattern, self._default_ttl)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self._enabled:
            return None

        start_time = time.perf_counter()
        key = generate_cache_key(endpoint, params)

        try:
            entry = self._backend.get(key)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if entry is not None:
                self._stats.record_hit(elapsed_ms)
                if isinstance(entry.value, dict):
                    return entry.value
                return {"data": entry.value}

            self._stats.record_miss(elapsed_ms)
            return None

        except Exception:
            self._stats.record_error()
            return None

    def set(
        self,
        endpoint: str,
        value: dict[str, Any],
        params: dict[str, Any] | None = None,
        ttl: float | None = None,
    ) -> bool:
        if not self._enabled:
            return False

        start_time = time.perf_counter()
        key = generate_cache_key(endpoint, params)

        if ttl is None:
            ttl = self.get_ttl_for_endpoint(endpoint)

        try:
            self._backend.set(key, value, ttl_seconds=ttl)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._stats.record_set(elapsed_ms)
            return True

        except Exception:
            self._stats.record_error()
            return False

    def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> bool:
        if not self._enabled:
            return False

        key = generate_cache_key(endpoint, params)

        try:
            result = self._backend.delete(key)
            if result:
                self._stats.record_delete()
            return result

        except Exception:
            self._stats.record_error()
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        count = 0
        for endpoint_pattern in self._ttl_policies:
            if pattern in endpoint_pattern:
                count += 1
        return count

    def clear(self) -> None:
        try:
            self._backend.clear()
        except Exception:
            self._stats.record_error()

    def get_stats_dict(self) -> dict[str, Any]:
        return self._stats.to_dict()

    def reset_stats(self) -> None:
        self._stats.reset()


class AsyncCacheManager:
    """Async cache manager for Redis backend."""

    def __init__(
        self,
        backend: CacheBackend | None = None,
        ttl_policies: dict[str, float] | None = None,
        default_ttl: float = DEFAULT_TTL,
        enabled: bool = True,
    ) -> None:
        self._sync_manager = CacheManager(
            backend=backend,
            ttl_policies=ttl_policies,
            default_ttl=default_ttl,
            enabled=enabled,
        )

    @property
    def backend(self) -> CacheBackend:
        return self._sync_manager.backend

    @property
    def stats(self) -> CacheStats:
        return self._sync_manager.stats

    @property
    def enabled(self) -> bool:
        return self._sync_manager.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._sync_manager.enabled = value

    def get_ttl_for_endpoint(self, endpoint: str) -> float:
        return self._sync_manager.get_ttl_for_endpoint(endpoint)

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self._sync_manager.enabled:
            return None

        start_time = time.perf_counter()
        key = generate_cache_key(endpoint, params)

        try:
            if hasattr(self.backend, "get_async"):
                entry = await self.backend.get_async(key)
            else:
                entry = self.backend.get(key)

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if entry is not None:
                self._sync_manager._stats.record_hit(elapsed_ms)
                if isinstance(entry.value, dict):
                    return entry.value
                return {"data": entry.value}

            self._sync_manager._stats.record_miss(elapsed_ms)
            return None

        except Exception:
            self._sync_manager._stats.record_error()
            return None

    async def set(
        self,
        endpoint: str,
        value: dict[str, Any],
        params: dict[str, Any] | None = None,
        ttl: float | None = None,
    ) -> bool:
        if not self._sync_manager.enabled:
            return False

        start_time = time.perf_counter()
        key = generate_cache_key(endpoint, params)

        if ttl is None:
            ttl = self.get_ttl_for_endpoint(endpoint)

        try:
            if hasattr(self.backend, "set_async"):
                await self.backend.set_async(key, value, ttl_seconds=ttl)
            else:
                self.backend.set(key, value, ttl_seconds=ttl)

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._sync_manager._stats.record_set(elapsed_ms)
            return True

        except Exception:
            self._sync_manager._stats.record_error()
            return False

    async def delete(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> bool:
        if not self._sync_manager.enabled:
            return False

        key = generate_cache_key(endpoint, params)

        try:
            if hasattr(self.backend, "delete_async"):
                result = await self.backend.delete_async(key)
            else:
                result = self.backend.delete(key)

            if result:
                self._sync_manager._stats.record_delete()
            return result

        except Exception:
            self._sync_manager._stats.record_error()
            return False

    async def clear(self) -> None:
        try:
            if hasattr(self.backend, "clear_async"):
                await self.backend.clear_async()
            else:
                self.backend.clear()
        except Exception:
            self._sync_manager._stats.record_error()

    async def close(self) -> None:
        if hasattr(self.backend, "close"):
            await self.backend.close()

    def get_stats_dict(self) -> dict[str, Any]:
        return self._sync_manager.get_stats_dict()

    def reset_stats(self) -> None:
        self._sync_manager.reset_stats()
