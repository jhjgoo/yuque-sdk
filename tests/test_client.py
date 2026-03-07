"""Tests for Yuque API client."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from yuque.client import YuqueClient
from yuque.exceptions import (
    AuthenticationError,
    InvalidArgumentError,
    NetworkError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
    YuqueError,
)


class TestYuqueClient:
    """Tests for YuqueClient class."""

    def test_init(self):
        """Test client initialization."""
        client = YuqueClient(token="test-token")
        assert client._token == "test-token"
        assert client._timeout == 30.0
        assert client._max_retries == 3

    def test_init_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = YuqueClient(token="test-token", timeout=60.0)
        assert client._timeout == 60.0

    def test_init_custom_retries(self):
        """Test client initialization with custom retries."""
        client = YuqueClient(token="test-token", max_retries=5)
        assert client._max_retries == 5

    def test_get_headers(self):
        """Test header generation."""
        client = YuqueClient(token="test-token")
        headers = client._get_headers()
        assert headers["X-Auth-Token"] == "test-token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestExceptionMapping:
    """Tests for exception mapping based on status codes."""

    def test_authentication_error(self):
        """Test 401 error mapping."""
        error = AuthenticationError()
        assert error.status_code == 401

    def test_permission_denied_error(self):
        """Test 403 error mapping."""
        error = PermissionDeniedError()
        assert error.status_code == 403

    def test_not_found_error(self):
        """Test 404 error mapping."""
        error = NotFoundError()
        assert error.status_code == 404

    def test_invalid_argument_error(self):
        """Test 400 error mapping."""
        error = InvalidArgumentError()
        assert error.status_code == 400

    def test_rate_limit_error(self):
        """Test 429 error mapping."""
        error = RateLimitError()
        assert error.status_code == 429

    def test_server_error(self):
        """Test 500+ error mapping."""
        error = ServerError(status_code=500)
        assert error.status_code == 500


class TestContextManager:
    """Tests for context manager usage."""

    def test_sync_context_manager(self):
        """Test synchronous context manager."""
        with YuqueClient(token="test-token") as client:
            assert client._sync_client is not None

    def test_async_context_manager(self):
        """Test asynchronous context manager."""
        import asyncio

        async def test_async():
            async with YuqueClient(token="test-token") as client:
                assert client._async_client is not None

        asyncio.run(test_async())


class TestAPIAccess:
    """Tests for API endpoint access."""

    def test_user_api_access(self):
        """Test user API property."""
        client = YuqueClient(token="test-token")
        assert hasattr(client, "user")
        assert client.user.__class__.__name__ == "UserAPI"

    def test_group_api_access(self):
        """Test group API property."""
        client = YuqueClient(token="test-token")
        assert hasattr(client, "group")
        assert client.group.__class__.__name__ == "GroupAPI"

    def test_repo_api_access(self):
        """Test repo API property."""
        client = YuqueClient(token="test-token")
        assert hasattr(client, "repo")
        assert client.repo.__class__.__name__ == "RepoAPI"

    def test_doc_api_access(self):
        """Test doc API property."""
        client = YuqueClient(token="test-token")
        assert hasattr(client, "doc")
        assert client.doc.__class__.__name__ == "DocAPI"

    def test_search_api_access(self):
        """Test search API property."""
        client = YuqueClient(token="test-token")
        assert hasattr(client, "search")
        assert client.search.__class__.__name__ == "SearchAPI"


class TestModels:
    """Tests for Pydantic models."""

    def test_user_model(self):
        """Test User model creation."""
        from yuque.models import User

        user_data = {
            "id": 123,
            "login": "testuser",
            "name": "Test User",
            "avatar_url": "https://example.com/avatar.png",
        }
        user = User(**user_data)
        assert user.id == 123
        assert user.login == "testuser"
        assert user.name == "Test User"

    def test_group_model(self):
        """Test Group model creation."""
        from yuque.models import Group

        group_data = {
            "id": 456,
            "login": "testgroup",
            "name": "Test Group",
            "description": "A test group",
            "owner_id": 123,  # Required field
        }
        group = Group(**group_data)
        assert group.id == 456
        assert group.login == "testgroup"

    def test_repository_model(self):
        """Test Repository model creation."""
        from yuque.models import Repository

        repo_data = {
            "id": 789,
            "type": "Book",
            "slug": "test-repo",
            "name": "Test Repository",
            "public": 0,
            "creator_id": 123,  # Required field
        }
        repo = Repository(**repo_data)
        assert repo.id == 789
        assert repo.slug == "test-repo"

    def test_document_model(self):
        """Test Document model creation."""
        from yuque.models import Document

        doc_data = {
            "id": 111,
            "slug": "test-doc",
            "title": "Test Document",
            "body": "# Hello World",
            "body_format": 1,
            "user_id": 123,
            "book_id": 789,
            "creator_id": 123,  # Required field
        }
        doc = Document(**doc_data)
        assert doc.id == 111
        assert doc.title == "Test Document"


class TestPaginationMeta:
    """Tests for pagination metadata."""

    def test_pagination_meta_creation(self):
        """Test PaginationMeta model."""
        from yuque.models import PaginationMeta

        meta = PaginationMeta(page=1, per_page=20, total=100, total_pages=5)
        assert meta.page == 1
        assert meta.per_page == 20
        assert meta.total == 100
        assert meta.total_pages == 5


class TestCacheInitialization:
    """Tests for cache initialization."""

    def test_init_with_cache_manager(self):
        """Test initialization with CacheManager instance."""
        from yuque.cache import CacheManager

        cache = CacheManager(enabled=True)
        client = YuqueClient(token="test-token", cache=cache)
        assert client._cache is cache
        assert client._async_cache is not None

    def test_init_with_cache_backend(self):
        """Test initialization with cache backend."""
        from yuque.cache import MemoryCacheBackend

        backend = MemoryCacheBackend()
        client = YuqueClient(token="test-token", cache_backend=backend)
        assert client._cache is not None
        assert client._async_cache is not None

    def test_init_without_cache(self):
        """Test initialization without cache."""
        client = YuqueClient(token="test-token")
        assert client._cache is None
        assert client._async_cache is None


class TestHTTPMethods:
    """Tests for HTTP request methods."""

    def test_get_method_success(self):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "test"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request("GET", "/api/test")
                assert result == {"data": "test"}

    def test_post_method_success(self):
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.is_success = True
        mock_response.json.return_value = {"id": 1}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request("POST", "/api/test", json_data={"name": "test"})
                assert result == {"id": 1}

    def test_put_method_success(self):
        """Test successful PUT request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"updated": True}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request("PUT", "/api/test/1", json_data={"name": "updated"})
                assert result == {"updated": True}

    def test_delete_method_success(self):
        """Test successful DELETE request."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.is_success = True
        mock_response.json.return_value = {}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request("DELETE", "/api/test/1")
                assert result == {}

    def test_get_method_with_params(self):
        """Test GET request with query parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"items": []}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request("GET", "/api/test", params={"page": 1, "limit": 10})
                assert result == {"items": []}

    def test_request_with_cache_hit(self):
        """Test GET request with cache hit."""
        from yuque.cache import CacheManager

        cache = CacheManager(enabled=True)
        cache.set("/api/test", {"cached": "data"}, None)

        with YuqueClient(token="test-token", cache=cache) as client:
            result = client._request("GET", "/api/test")
            assert result == {"cached": "data"}

    def test_request_sets_cache(self):
        """Test that successful GET request sets cache."""
        from yuque.cache import CacheManager

        cache = CacheManager(enabled=True)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "fresh"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token", cache=cache) as client:
                result = client._request("GET", "/api/test")
                assert result == {"data": "fresh"}
                # Verify cache was set
                cached = cache.get("/api/test", None)
                assert cached == {"data": "fresh"}


class TestHandleResponse:
    """Tests for response handling."""

    def test_handle_response_success(self):
        """Test successful response handling."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "test"}

        client = YuqueClient(token="test-token")
        result = client._handle_response(mock_response)
        assert result == {"data": "test"}

    def test_handle_response_success_no_json(self):
        """Test successful response with no JSON body."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.is_success = True
        mock_response.json.side_effect = Exception("No JSON")

        client = YuqueClient(token="test-token")
        result = client._handle_response(mock_response)
        assert result == {}

    def test_handle_response_400_error(self):
        """Test 400 Bad Request error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_response.text = "Invalid request"

        client = YuqueClient(token="test-token")
        with pytest.raises(InvalidArgumentError):
            client._handle_response(mock_response)

    def test_handle_response_401_error(self):
        """Test 401 Unauthorized error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_response.text = "Unauthorized"

        client = YuqueClient(token="test-token")
        with pytest.raises(AuthenticationError):
            client._handle_response(mock_response)

    def test_handle_response_403_error(self):
        """Test 403 Forbidden error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Forbidden"}
        mock_response.text = "Forbidden"

        client = YuqueClient(token="test-token")
        with pytest.raises(PermissionDeniedError):
            client._handle_response(mock_response)

    def test_handle_response_404_error(self):
        """Test 404 Not Found error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.text = "Not found"

        client = YuqueClient(token="test-token")
        with pytest.raises(NotFoundError):
            client._handle_response(mock_response)

    def test_handle_response_422_error(self):
        """Test 422 Validation error."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Validation failed"}
        mock_response.text = "Validation failed"

        client = YuqueClient(token="test-token")
        with pytest.raises(ValidationError):
            client._handle_response(mock_response)

    def test_handle_response_429_error(self):
        """Test 429 Rate Limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {"Retry-After": "60"}

        client = YuqueClient(token="test-token")
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(mock_response)
        assert exc_info.value.retry_after == 60

    def test_handle_response_429_error_no_retry_after(self):
        """Test 429 Rate Limit error without Retry-After header."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {}

        client = YuqueClient(token="test-token")
        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(mock_response)
        assert exc_info.value.retry_after is None

    def test_handle_response_500_error(self):
        """Test 500 Server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_response.text = "Internal server error"

        client = YuqueClient(token="test-token")
        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)
        assert exc_info.value.status_code == 500

    def test_handle_response_502_error(self):
        """Test 502 Bad Gateway error."""
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.is_success = False
        mock_response.json.return_value = {"error": "Bad gateway"}
        mock_response.text = "Bad gateway"

        client = YuqueClient(token="test-token")
        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)
        assert exc_info.value.status_code == 502

    def test_handle_response_unknown_error(self):
        """Test unknown HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 418  # I'm a teapot
        mock_response.is_success = False
        mock_response.json.return_value = {}
        mock_response.text = "I'm a teapot"

        client = YuqueClient(token="test-token")
        with pytest.raises(YuqueError) as exc_info:
            client._handle_response(mock_response)
        assert exc_info.value.status_code == 418

    def test_handle_response_error_no_json(self):
        """Test error response with no JSON body uses text."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.json.side_effect = Exception("No JSON")
        mock_response.text = "Server Error"

        client = YuqueClient(token="test-token")
        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)
        assert "Server Error" in str(exc_info.value)


class TestNetworkErrors:
    """Tests for network error handling."""

    def test_network_error(self):
        """Test network error handling."""
        import httpx

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.side_effect = httpx.NetworkError("Connection failed")
            mock_client_class.return_value = mock_client

            with pytest.raises(NetworkError):
                with YuqueClient(token="test-token") as client:
                    client._request("GET", "/api/test")

    def test_timeout_error(self):
        """Test timeout error handling."""
        import httpx

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value = mock_client

            with pytest.raises(NetworkError):
                with YuqueClient(token="test-token") as client:
                    client._request("GET", "/api/test")


class TestAsyncHTTPMethods:
    """Tests for async HTTP request methods."""

    @pytest.mark.asyncio
    async def test_async_get_method_success(self):
        """Test successful async GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "async"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                result = await client._request_async("GET", "/api/test")
                assert result == {"data": "async"}

    @pytest.mark.asyncio
    async def test_async_post_method_success(self):
        """Test successful async POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.is_success = True
        mock_response.json.return_value = {"id": 1}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                result = await client._request_async(
                    "POST", "/api/test", json_data={"name": "test"}
                )
                assert result == {"id": 1}

    @pytest.mark.asyncio
    async def test_async_put_method_success(self):
        """Test successful async PUT request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"updated": True}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                result = await client._request_async(
                    "PUT", "/api/test/1", json_data={"name": "updated"}
                )
                assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_async_delete_method_success(self):
        """Test successful async DELETE request."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.is_success = True
        mock_response.json.return_value = {}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                result = await client._request_async("DELETE", "/api/test/1")
                assert result == {}

    @pytest.mark.asyncio
    async def test_async_request_with_cache_hit(self):
        """Test async GET request with cache hit."""
        from yuque.cache import AsyncCacheManager, MemoryCacheBackend

        backend = MemoryCacheBackend()
        cache = AsyncCacheManager(backend=backend)

        await cache.set("/api/test", {"cached": "async"}, None)

        client = YuqueClient(token="test-token")
        client._async_cache = cache

        result = await client._request_async("GET", "/api/test")
        assert result == {"cached": "async"}

    @pytest.mark.asyncio
    async def test_async_network_error(self):
        """Test async network error handling."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(side_effect=httpx.NetworkError("Connection failed"))
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                with pytest.raises(NetworkError):
                    await client._request_async("GET", "/api/test")

    @pytest.mark.asyncio
    async def test_async_timeout_error(self):
        """Test async timeout error handling."""
        import httpx

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
            mock_client.aclose = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            async with YuqueClient(token="test-token") as client:
                with pytest.raises(NetworkError):
                    await client._request_async("GET", "/api/test")


class TestPaginatedRequests:
    """Tests for paginated request methods."""

    def test_request_paginated_single_page(self):
        """Test paginated request with single page."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {
            "data": [{"id": 1}, {"id": 2}],
            "meta": {"page": 1, "per_page": 20, "total": 2, "total_pages": 1},
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request_paginated("GET", "/api/test")
                assert len(result) == 2

    def test_request_paginated_multiple_pages(self):
        """Test paginated request with multiple pages."""
        call_count = [0]

        def mock_request(*args, **kwargs):
            call_count[0] += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True

            if call_count[0] == 1:
                mock_response.json.return_value = {
                    "data": [{"id": 1}],
                    "meta": {"page": 1, "per_page": 1, "total": 2, "total_pages": 2},
                }
            else:
                mock_response.json.return_value = {
                    "data": [{"id": 2}],
                    "meta": {"page": 2, "per_page": 1, "total": 2, "total_pages": 2},
                }
            return mock_response

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.side_effect = mock_request
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request_paginated("GET", "/api/test", params={"per_page": 1})
                assert len(result) == 2
                assert result[0]["id"] == 1
                assert result[1]["id"] == 2

    def test_request_paginated_no_meta(self):
        """Test paginated request without meta."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"data": [{"id": 1}, {"id": 2}]}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request_paginated("GET", "/api/test")
                assert len(result) == 2

    def test_request_paginated_with_initial_page(self):
        """Test paginated request with initial page parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {
            "data": [{"id": 1}],
            "meta": {"page": 2, "per_page": 10, "total": 1, "total_pages": 1},
        }

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client._request_paginated("GET", "/api/test", params={"page": 2})
                assert len(result) == 1


class TestParsePaginatedResponse:
    """Tests for parsing paginated responses."""

    def test_parse_paginated_response_with_meta(self):
        """Test parsing paginated response with meta."""
        from yuque.models import PaginatedResponse

        client = YuqueClient(token="test-token")
        response = {
            "data": [{"id": 1}, {"id": 2}],
            "meta": {"page": 1, "per_page": 20, "total": 2, "total_pages": 1},
        }

        result = client._parse_paginated_response(response)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 2
        assert result.meta is not None

    def test_parse_paginated_response_without_meta(self):
        """Test parsing paginated response without meta."""
        from yuque.models import PaginatedResponse

        client = YuqueClient(token="test-token")
        response = {"data": [{"id": 1}]}

        result = client._parse_paginated_response(response)
        assert isinstance(result, PaginatedResponse)
        assert len(result.data) == 1
        assert result.meta is None

    def test_parse_paginated_response_single_item(self):
        """Test parsing paginated response with single item."""
        client = YuqueClient(token="test-token")
        response = {"data": {"id": 1}}

        result = client._parse_paginated_response(response)
        assert len(result.data) == 1
        assert result.data[0] == {"id": 1}


class TestHelloMethod:
    """Tests for hello method."""

    def test_hello_method(self):
        """Test hello API method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"message": "Hello from Yuque!"}

        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            with YuqueClient(token="test-token") as client:
                result = client.hello()
                assert result == {"message": "Hello from Yuque!"}


class TestClientLifecycle:
    """Tests for client lifecycle methods."""

    def test_close_sync_client(self):
        """Test closing sync client."""
        with YuqueClient(token="test-token") as client:
            assert client._sync_client is not None
        assert client._sync_client is None

    def test_close_sync_client_when_none(self):
        """Test closing sync client when already None."""
        client = YuqueClient(token="test-token")
        client._close_sync_client()  # Should not raise
        assert client._sync_client is None

    def test_get_sync_client_creates_client(self):
        """Test _get_sync_client creates client when None."""
        client = YuqueClient(token="test-token")
        assert client._sync_client is None
        sync_client = client._get_sync_client()
        assert sync_client is not None
        client._close_sync_client()

    def test_get_sync_client_returns_existing(self):
        """Test _get_sync_client returns existing client."""
        client = YuqueClient(token="test-token")
        first = client._get_sync_client()
        second = client._get_sync_client()
        assert first is second
        client._close_sync_client()


class TestAsyncClientLifecycle:
    """Tests for async client lifecycle methods."""

    @pytest.mark.asyncio
    async def test_close_async_client(self):
        """Test closing async client."""
        async with YuqueClient(token="test-token") as client:
            assert client._async_client is not None
        assert client._async_client is None

    @pytest.mark.asyncio
    async def test_close_async_client_when_none(self):
        """Test closing async client when already None."""
        client = YuqueClient(token="test-token")
        await client._close_async_client()  # Should not raise
        assert client._async_client is None

    @pytest.mark.asyncio
    async def test_get_async_client_creates_client(self):
        """Test _get_async_client creates client when None."""
        client = YuqueClient(token="test-token")
        assert client._async_client is None
        async_client = client._get_async_client()
        assert async_client is not None
        await client._close_async_client()

    @pytest.mark.asyncio
    async def test_get_async_client_returns_existing(self):
        """Test _get_async_client returns existing client."""
        client = YuqueClient(token="test-token")
        first = client._get_async_client()
        second = client._get_async_client()
        assert first is second
        await client._close_async_client()


class TestPropertyAccessors:
    """Tests for property accessors."""

    def test_user_property_returns_user_api(self):
        """Test user property returns UserAPI."""
        client = YuqueClient(token="test-token")
        user = client.user
        assert user.__class__.__name__ == "UserAPI"

    def test_group_property_returns_group_api(self):
        """Test group property returns GroupAPI."""
        client = YuqueClient(token="test-token")
        group = client.group
        assert group.__class__.__name__ == "GroupAPI"

    def test_repo_property_returns_repo_api(self):
        """Test repo property returns RepoAPI."""
        client = YuqueClient(token="test-token")
        repo = client.repo
        assert repo.__class__.__name__ == "RepoAPI"

    def test_doc_property_returns_doc_api(self):
        """Test doc property returns DocAPI."""
        client = YuqueClient(token="test-token")
        doc = client.doc
        assert doc.__class__.__name__ == "DocAPI"

    def test_search_property_returns_search_api(self):
        """Test search property returns SearchAPI."""
        client = YuqueClient(token="test-token")
        search = client.search
        assert search.__class__.__name__ == "SearchAPI"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
