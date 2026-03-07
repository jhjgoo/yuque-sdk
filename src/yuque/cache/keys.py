"""Cache key generation utilities."""

from __future__ import annotations

import hashlib
from typing import Any


def generate_cache_key(
    endpoint: str,
    params: dict[str, Any] | None = None,
    prefix: str = "yuque",
) -> str:
    """Generate a unique cache key for an API request.

    Args:
        endpoint: API endpoint path.
        params: Optional request parameters.
        prefix: Optional prefix for namespacing.

    Returns:
        Unique cache key string.
    """
    parts = [prefix, endpoint]

    if params:
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        parts.append(param_str)

    key_base = ":".join(parts)

    if len(key_base) > 200:
        hash_suffix = hashlib.md5(key_base.encode()).hexdigest()[:16]
        return f"{prefix}:{endpoint}:{hash_suffix}"

    return key_base


def get_endpoint_pattern(endpoint: str) -> str:
    """Determine endpoint pattern for TTL matching.

    Args:
        endpoint: The API endpoint path.

    Returns:
        Pattern string for TTL policy lookup.
    """
    endpoint_lower = endpoint.lower()

    if endpoint_lower.startswith("/user"):
        return "/user"

    if "/repos/" in endpoint_lower and "/docs" in endpoint_lower:
        return "/repos/*/docs"

    if "/repos/" in endpoint_lower or endpoint_lower.startswith("/repos"):
        return "/repos"

    if "/docs/" in endpoint_lower:
        return "/docs/"

    if "/search" in endpoint_lower:
        return "/search"

    if "/groups" in endpoint_lower:
        return "/groups"

    return "default"
