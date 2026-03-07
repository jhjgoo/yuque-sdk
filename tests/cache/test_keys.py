"""Tests for cache key generation utilities."""

from __future__ import annotations

import hashlib

import pytest

from yuque.cache.keys import generate_cache_key, get_endpoint_pattern


class TestGenerateCacheKey:
    """Tests for generate_cache_key function."""

    def test_generate_cache_key_simple_endpoint(self) -> None:
        """Simple endpoint name."""
        key = generate_cache_key("/users/me")

        assert key == "yuque:/users/me"

    def test_generate_cache_key_with_params(self) -> None:
        """Include parameters."""
        key = generate_cache_key("/repos/123", params={"page": 1, "limit": 20})

        assert "yuque:/repos/123" in key
        assert "limit=20" in key
        assert "page=1" in key

    def test_generate_cache_key_param_sorting(self) -> None:
        """Deterministic ordering of parameters."""
        key1 = generate_cache_key("/docs", params={"z": "last", "a": "first", "m": "middle"})
        key2 = generate_cache_key("/docs", params={"m": "middle", "a": "first", "z": "last"})

        assert key1 == key2

    def test_generate_cache_key_long_key_hashing(self) -> None:
        """MD5 for long keys (>200 chars)."""
        # Create a very long endpoint with many params
        long_params = {f"param_{i}": f"value_{i}_very_long_string" for i in range(50)}
        key = generate_cache_key("/very/long/endpoint/path", params=long_params)

        # Should be truncated and hashed
        assert len(key) < 200
        # Should contain prefix and endpoint with hash
        assert key.startswith("yuque:/very/long/endpoint/path:")
        # Hash should be 16 chars (truncated MD5)
        parts = key.split(":")
        assert len(parts[-1]) == 16

    def test_generate_cache_key_with_prefix(self) -> None:
        """Prefix applied."""
        key = generate_cache_key("/users/me", prefix="myapp")

        assert key == "myapp:/users/me"

    def test_generate_cache_key_custom_prefix_with_params(self) -> None:
        """Custom prefix with parameters."""
        key = generate_cache_key("/docs", params={"id": 123}, prefix="custom_cache")

        assert key.startswith("custom_cache:/docs")

    def test_empty_params(self) -> None:
        """No parameters."""
        key = generate_cache_key("/users/me", params=None)

        assert key == "yuque:/users/me"

    def test_empty_params_dict(self) -> None:
        """Empty parameters dict."""
        key = generate_cache_key("/users/me", params={})

        assert key == "yuque:/users/me"

    def test_special_characters_in_params(self) -> None:
        """URL encoding of special characters."""
        key = generate_cache_key("/search", params={"q": "hello world&test=1"})

        # Should contain the special characters (not URL encoded at this level)
        assert "q=hello world&test=1" in key

    def test_unicode_in_params(self) -> None:
        """Unicode characters in parameters."""
        key = generate_cache_key("/search", params={"q": "中文测试"})

        assert "中文测试" in key

    def test_numeric_params(self) -> None:
        """Numeric parameter values."""
        key = generate_cache_key("/repos", params={"id": 12345, "page": 1})

        assert "id=12345" in key
        assert "page=1" in key

    def test_boolean_params(self) -> None:
        """Boolean parameter values."""
        key = generate_cache_key("/docs", params={"public": True, "draft": False})

        assert "public=True" in key
        assert "draft=False" in key

    def test_consistency(self) -> None:
        """Same inputs produce same key."""
        params = {"a": 1, "b": 2, "c": 3}

        key1 = generate_cache_key("/test", params=params)
        key2 = generate_cache_key("/test", params=params)

        assert key1 == key2

    def test_hash_deterministic(self) -> None:
        """Long key hashing is deterministic."""
        long_params = {f"key_{i}": f"value_{i}" * 10 for i in range(30)}

        key1 = generate_cache_key("/long/endpoint", params=long_params)
        key2 = generate_cache_key("/long/endpoint", params=long_params)

        assert key1 == key2


class TestGetEndpointPattern:
    """Tests for get_endpoint_pattern function."""

    def test_get_endpoint_pattern_user(self) -> None:
        """User endpoint."""
        assert get_endpoint_pattern("/user") == "/user"
        assert get_endpoint_pattern("/users/me") == "/user"
        assert get_endpoint_pattern("/USER/123") == "/user"

    def test_get_endpoint_pattern_repos(self) -> None:
        """Repository endpoints."""
        assert get_endpoint_pattern("/repos") == "/repos"
        assert get_endpoint_pattern("/REPOS/123") == "/repos"
        assert get_endpoint_pattern("/api/repos/456") == "/repos"

    def test_get_endpoint_pattern_docs(self) -> None:
        """Document endpoints."""
        assert get_endpoint_pattern("/docs/123") == "/docs/"
        assert get_endpoint_pattern("/DOCS/abc") == "/docs/"

    def test_get_endpoint_pattern_repo_docs(self) -> None:
        """Repository docs endpoints."""
        assert get_endpoint_pattern("/repos/123/docs") == "/repos/*/docs"
        assert get_endpoint_pattern("/REPOS/456/DOCS") == "/repos/*/docs"

    def test_get_endpoint_pattern_search(self) -> None:
        """Search endpoint."""
        assert get_endpoint_pattern("/search") == "/search"
        assert get_endpoint_pattern("/SEARCH") == "/search"
        assert get_endpoint_pattern("/api/search?q=test") == "/search"

    def test_get_endpoint_pattern_groups(self) -> None:
        """Groups endpoint."""
        assert get_endpoint_pattern("/groups") == "/groups"
        assert get_endpoint_pattern("/GROUPS/mygroup") == "/groups"
        assert get_endpoint_pattern("/api/groups/123") == "/groups"

    def test_get_endpoint_pattern_default(self) -> None:
        """Unknown endpoint returns default."""
        assert get_endpoint_pattern("/unknown") == "default"
        assert get_endpoint_pattern("/api/v2/custom") == "default"
        assert get_endpoint_pattern("") == "default"

    def test_endpoint_pattern_case_insensitive(self) -> None:
        """Pattern matching is case insensitive."""
        assert get_endpoint_pattern("/USER") == "/user"
        assert get_endpoint_pattern("/RePoS/123") == "/repos"
        assert get_endpoint_pattern("/SEARCH") == "/search"

    def test_endpoint_pattern_priority(self) -> None:
        """More specific patterns take priority."""
        # /repos/*/docs should match before /repos
        assert get_endpoint_pattern("/repos/123/docs") == "/repos/*/docs"
        assert get_endpoint_pattern("/repos/123") == "/repos"


class TestCacheKeyEdgeCases:
    """Edge case tests for cache key generation."""

    def test_none_param_value(self) -> None:
        """None parameter value."""
        key = generate_cache_key("/test", params={"filter": None})

        assert "filter=None" in key

    def test_list_param_value(self) -> None:
        """List parameter value."""
        key = generate_cache_key("/test", params={"ids": [1, 2, 3]})

        assert "ids=[1, 2, 3]" in key

    def test_dict_param_value(self) -> None:
        """Dict parameter value."""
        key = generate_cache_key("/test", params={"meta": {"key": "value"}})

        assert "meta" in key

    def test_nested_path_endpoint(self) -> None:
        """Deeply nested endpoint path."""
        key = generate_cache_key("/users/123/repos/456/docs/789")

        assert key == "yuque:/users/123/repos/456/docs/789"

    def test_endpoint_with_query_string(self) -> None:
        """Endpoint that includes query string."""
        # Endpoint is treated as-is, params are appended
        key = generate_cache_key("/search?q=test", params={"page": 1})

        assert "search?q=test" in key
        assert "page=1" in key

    def test_empty_endpoint(self) -> None:
        """Empty endpoint string."""
        key = generate_cache_key("")

        assert key == "yuque:"

    def test_slash_only_endpoint(self) -> None:
        """Endpoint is just slash."""
        key = generate_cache_key("/")

        assert key == "yuque:/"

    def test_prefix_with_colon(self) -> None:
        """Prefix already contains colon."""
        key = generate_cache_key("/test", prefix="yuque:")

        assert key == "yuque::/test"

    def test_multiple_same_keys_in_params(self) -> None:
        """Dict cannot have duplicate keys, but test behavior."""
        # In Python, dict keys are unique, so this tests normal behavior
        params = {"key": "value"}
        key = generate_cache_key("/test", params=params)

        assert "key=value" in key
