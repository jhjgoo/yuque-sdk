"""Cache module for Yuque SDK."""

from .backend import CacheBackend, CacheEntry
from .manager import DEFAULT_TTL, TTL_POLICIES, AsyncCacheManager, CacheManager
from .memory import MemoryCacheBackend
from .stats import CacheStats, StatsTracker

__all__ = [
    "CacheBackend",
    "CacheEntry",
    "CacheManager",
    "AsyncCacheManager",
    "MemoryCacheBackend",
    "CacheStats",
    "StatsTracker",
    "TTL_POLICIES",
    "DEFAULT_TTL",
]

# Conditional import - RedisCacheBackend is only available if redis is installed
try:
    from .redis_backend import RedisCacheBackend  # noqa: F401

    __all__.append("RedisCacheBackend")
except ImportError:
    pass
