"""Tests for Redis cache backend implementation."""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yuque.cache.backend import CacheEntry
from yuque.cache.redis_backend import RedisCacheBackend


class TestRedisCacheBackendInit:
    """Tests for RedisCacheBackend initialization."""

    def test_init_with_url(self) -> None:
        """Initialize with connection URL."""
        backend = RedisCacheBackend(url="redis://localhost:6379/1")

        assert backend._url == "redis://localhost:6379/1"
        assert backend._redis is None
        assert backend._key_prefix == "yuque:"
        assert backend._owns_client is True

    def test_init_with_existing_client(self) -> None:
        """Use existing Redis client."""
        mock_client = MagicMock()
        backend = RedisCacheBackend(redis_client=mock_client)

        assert backend._redis is mock_client
        assert backend._owns_client is False

    def test_init_with_custom_prefix(self) -> None:
        """Initialize with custom key prefix."""
        backend = RedisCacheBackend(key_prefix="custom:")

        assert backend._key_prefix == "custom:"

    def test_name_property(self) -> None:
        """Backend name is 'redis'."""
        backend = RedisCacheBackend()
        assert backend.name == "redis"


class TestRedisCacheBackendClientCreation:
    """Tests for lazy client creation."""

    @pytest.mark.asyncio
    async def test_lazy_client_creation(self) -> None:
        """Client created on first use when redis package is available."""
        backend = RedisCacheBackend(url="redis://localhost:6379/0")

        assert backend._redis is None
        assert backend._owns_client is True

        mock_redis = AsyncMock()
        mock_aioredis = MagicMock()
        mock_aioredis.from_url.return_value = mock_redis

        with patch.dict("sys.modules", {"redis": MagicMock(), "redis.asyncio": mock_aioredis}):
            client = await backend._get_client()
            assert client is not None
            assert backend._redis is client

    @pytest.mark.asyncio
    async def test_client_reuse(self) -> None:
        """Client is reused on subsequent calls."""
        mock_client = AsyncMock()
        backend = RedisCacheBackend(redis_client=mock_client)

        client1 = await backend._get_client()
        client2 = await backend._get_client()

        assert client1 is mock_client
        assert client2 is mock_client


class TestRedisCacheBackendKeyPrefixing:
    """Tests for key prefixing."""

    def test_key_prefixing_default(self) -> None:
        """Keys have default prefix applied."""
        backend = RedisCacheBackend()
        assert backend._make_key("mykey") == "yuque:mykey"

    def test_key_prefixing_custom(self) -> None:
        """Keys have custom prefix applied."""
        backend = RedisCacheBackend(key_prefix="myapp:")
        assert backend._make_key("mykey") == "myapp:mykey"

    def test_key_prefixing_nested(self) -> None:
        """Nested keys are prefixed correctly."""
        backend = RedisCacheBackend()
        assert backend._make_key("user:123:profile") == "yuque:user:123:profile"


class TestRedisCacheBackendGet:
    """Tests for get_async operation."""

    @pytest.mark.asyncio
    async def test_get_async_success(self) -> None:
        """Successful get operation."""
        mock_client = AsyncMock()
        now = datetime.now()
        cached_data = {
            "value": {"name": "test"},
            "created_at": now.isoformat(),
            "expires_at": None,
            "ttl_seconds": None,
        }
        mock_client.get = AsyncMock(return_value=json.dumps(cached_data).encode())

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("test_key")

        assert result is not None
        assert result.key == "test_key"
        assert result.value == {"name": "test"}
        mock_client.get.assert_called_once_with("yuque:test_key")

    @pytest.mark.asyncio
    async def test_get_async_miss(self) -> None:
        """Key not found returns None."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=None)

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("missing_key")

        assert result is None
        mock_client.get.assert_called_once_with("yuque:missing_key")

    @pytest.mark.asyncio
    async def test_get_async_deserialization_error(self) -> None:
        """Invalid JSON handling returns None."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=b"invalid json{")

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("bad_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_async_with_ttl(self) -> None:
        """Get entry with TTL metadata."""
        mock_client = AsyncMock()
        now = datetime.now()
        cached_data = {
            "value": "data",
            "created_at": now.isoformat(),
            "expires_at": None,
            "ttl_seconds": 3600,
        }
        mock_client.get = AsyncMock(return_value=json.dumps(cached_data).encode())

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("ttl_key")

        assert result is not None
        assert result.ttl_seconds == 3600

    @pytest.mark.asyncio
    async def test_get_async_connection_error(self) -> None:
        """Connection error returns None."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=ConnectionError("Redis unreachable"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("error_key")

        assert result is None


class TestRedisCacheBackendSet:
    """Tests for set_async operation."""

    @pytest.mark.asyncio
    async def test_set_async_without_ttl(self) -> None:
        """Set without expiration."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(return_value=True)

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.set_async("test_key", {"data": "value"})

        mock_client.set.assert_called_once()
        call_args = mock_client.set.call_args
        assert call_args[0][0] == "yuque:test_key"

        # Verify JSON structure
        stored_data = json.loads(call_args[0][1])
        assert stored_data["value"] == {"data": "value"}
        assert stored_data["ttl_seconds"] is None

    @pytest.mark.asyncio
    async def test_set_async_with_ttl(self) -> None:
        """Set with TTL."""
        mock_client = AsyncMock()
        mock_client.setex = AsyncMock(return_value=True)

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.set_async("ttl_key", "value", ttl_seconds=300)

        mock_client.setex.assert_called_once()
        call_args = mock_client.setex.call_args
        assert call_args[0][0] == "yuque:ttl_key"
        assert call_args[0][1] == 300  # TTL in seconds

        stored_data = json.loads(call_args[0][2])
        assert stored_data["value"] == "value"
        assert stored_data["ttl_seconds"] == 300

    @pytest.mark.asyncio
    async def test_set_async_string_value(self) -> None:
        """Set string value."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(return_value=True)

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.set_async("str_key", "simple string")

        call_args = mock_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        assert stored_data["value"] == "simple string"

    @pytest.mark.asyncio
    async def test_set_async_complex_value(self) -> None:
        """Set complex nested value."""
        mock_client = AsyncMock()
        mock_client.set = AsyncMock(return_value=True)

        complex_value = {
            "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            "meta": {"total": 2, "page": 1},
        }

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.set_async("complex_key", complex_value)

        call_args = mock_client.set.call_args
        stored_data = json.loads(call_args[0][1])
        assert stored_data["value"] == complex_value


class TestRedisCacheBackendDelete:
    """Tests for delete_async operation."""

    @pytest.mark.asyncio
    async def test_delete_async_success(self) -> None:
        """Successful delete."""
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=1)

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.delete_async("test_key")

        assert result is True
        mock_client.delete.assert_called_once_with("yuque:test_key")

    @pytest.mark.asyncio
    async def test_delete_async_not_found(self) -> None:
        """Delete non-existent key returns False."""
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(return_value=0)

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.delete_async("missing_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_async_error(self) -> None:
        """Error during delete returns False."""
        mock_client = AsyncMock()
        mock_client.delete = AsyncMock(side_effect=Exception("Redis error"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.delete_async("error_key")

        assert result is False


class TestRedisCacheBackendExists:
    """Tests for exists_async operation."""

    @pytest.mark.asyncio
    async def test_exists_async_true(self) -> None:
        """Key exists."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(return_value=1)

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.exists_async("existing_key")

        assert result is True
        mock_client.exists.assert_called_once_with("yuque:existing_key")

    @pytest.mark.asyncio
    async def test_exists_async_false(self) -> None:
        """Key doesn't exist."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(return_value=0)

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.exists_async("missing_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_async_error(self) -> None:
        """Error during exists returns False."""
        mock_client = AsyncMock()
        mock_client.exists = AsyncMock(side_effect=Exception("Error"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.exists_async("error_key")

        assert result is False


class TestRedisCacheBackendClear:
    """Tests for clear_async operation."""

    @pytest.mark.asyncio
    async def test_clear_async_success(self) -> None:
        """Clear all keys with prefix."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=[b"yuque:key1", b"yuque:key2"])
        mock_client.delete = AsyncMock(return_value=2)

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.clear_async()

        mock_client.keys.assert_called_once_with("yuque:*")
        mock_client.delete.assert_called_once_with(b"yuque:key1", b"yuque:key2")

    @pytest.mark.asyncio
    async def test_clear_async_no_keys(self) -> None:
        """Clear with no keys does nothing."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=[])

        backend = RedisCacheBackend(redis_client=mock_client)
        await backend.clear_async()

        mock_client.keys.assert_called_once_with("yuque:*")
        mock_client.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_clear_async_error_silent(self) -> None:
        """Error during clear is silently ignored."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(side_effect=Exception("Redis error"))

        backend = RedisCacheBackend(redis_client=mock_client)
        # Should not raise
        await backend.clear_async()


class TestRedisCacheBackendGetSize:
    """Tests for get_size_async operation."""

    @pytest.mark.asyncio
    async def test_get_size_async(self) -> None:
        """Get number of keys."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=[b"yuque:key1", b"yuque:key2", b"yuque:key3"])

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_size_async()

        assert result == 3
        mock_client.keys.assert_called_once_with("yuque:*")

    @pytest.mark.asyncio
    async def test_get_size_async_empty(self) -> None:
        """Get size when empty."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(return_value=[])

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_size_async()

        assert result == 0

    @pytest.mark.asyncio
    async def test_get_size_async_error(self) -> None:
        """Error returns 0."""
        mock_client = AsyncMock()
        mock_client.keys = AsyncMock(side_effect=Exception("Error"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_size_async()

        assert result == 0


class TestRedisCacheBackendSyncMethods:
    """Tests that sync methods raise NotImplementedError."""

    def test_sync_get_raises_not_implemented(self) -> None:
        """Sync get throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError) as exc_info:
            backend.get("key")

        assert "get_async" in str(exc_info.value).lower()

    def test_sync_set_raises_not_implemented(self) -> None:
        """Sync set throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError) as exc_info:
            backend.set("key", "value")

        assert "set_async" in str(exc_info.value).lower()

    def test_sync_delete_raises_not_implemented(self) -> None:
        """Sync delete throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError) as exc_info:
            backend.delete("key")

        assert "delete_async" in str(exc_info.value).lower()

    def test_sync_exists_raises_not_implemented(self) -> None:
        """Sync exists throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError) as exc_info:
            backend.exists("key")

        assert "exists_async" in str(exc_info.value).lower()

    def test_sync_clear_raises_not_implemented(self) -> None:
        """Sync clear throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError):
            backend.clear()

    def test_sync_get_size_raises_not_implemented(self) -> None:
        """Sync get_size throws error."""
        backend = RedisCacheBackend()

        with pytest.raises(NotImplementedError):
            backend.get_size()


class TestRedisCacheBackendImportError:
    """Tests for missing redis package."""

    @pytest.mark.asyncio
    async def test_import_error_without_redis_package(self) -> None:
        """ImportError when redis not installed."""
        backend = RedisCacheBackend(url="redis://localhost:6379/0")

        with patch.dict("sys.modules", {"redis": None, "redis.asyncio": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'redis'")):
                with pytest.raises(ImportError) as exc_info:
                    await backend._get_client()

                assert "redis" in str(exc_info.value).lower()


class TestRedisCacheBackendClose:
    """Tests for connection cleanup."""

    @pytest.mark.asyncio
    async def test_connection_cleanup_owned_client(self) -> None:
        """close() works correctly for owned client."""
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()

        backend = RedisCacheBackend(redis_client=mock_client)
        # Override _owns_client since we passed a client
        backend._owns_client = True

        await backend.close()

        mock_client.close.assert_called_once()
        assert backend._redis is None

    @pytest.mark.asyncio
    async def test_connection_cleanup_not_owned(self) -> None:
        """close() does not close non-owned client."""
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()

        backend = RedisCacheBackend(redis_client=mock_client)
        # _owns_client is False when client is passed

        await backend.close()

        mock_client.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_close_with_none_client(self) -> None:
        """close() handles None client."""
        backend = RedisCacheBackend()
        backend._redis = None
        backend._owns_client = True

        # Should not raise
        await backend.close()


class TestRedisCacheBackendMemoryUsage:
    """Tests for memory usage."""

    def test_get_memory_usage_returns_negative(self) -> None:
        """Memory usage returns -1 (not supported)."""
        backend = RedisCacheBackend()
        assert backend.get_memory_usage() == -1


class TestRedisCacheBackendErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_error_handling_returns_none_on_exception(self) -> None:
        """Errors are handled silently, returning None."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("Unexpected error"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("error_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_error_handled(self) -> None:
        """Timeout errors are handled."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=TimeoutError("Connection timeout"))

        backend = RedisCacheBackend(redis_client=mock_client)
        result = await backend.get_async("timeout_key")

        assert result is None
