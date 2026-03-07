"""Core Yuque API client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from .api import DocAPI, GroupAPI, RepoAPI, SearchAPI, UserAPI
from .cache import AsyncCacheManager, CacheBackend, CacheManager
from .exceptions import (
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
from .models import PaginatedResponse

if TYPE_CHECKING:
    pass


BASE_URL = "https://www.yuque.com"


class YuqueClient:
    """
    Main client for interacting with the Yuque API.


    Args:
        token: Your Yuque API token
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum retry attempts (default: 3)
        cache: Optional CacheManager instance for caching support
        cache_backend: Optional cache backend for auto-creating CacheManager
    """

    _sync_client: httpx.Client | None
    _async_client: httpx.AsyncClient | None
    _cache: CacheManager | None
    _async_cache: AsyncCacheManager | None

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        cache: CacheManager | None = None,
        cache_backend: CacheBackend | None = None,
    ) -> None:
        self._token = token
        self._timeout = timeout
        self._max_retries = max_retries
        self._sync_client = None
        self._async_client = None

        if cache is not None:
            self._cache = cache
            self._async_cache = AsyncCacheManager(backend=cache.backend)
        elif cache_backend is not None:
            self._cache = CacheManager(backend=cache_backend)
            self._async_cache = AsyncCacheManager(backend=cache_backend)
        else:
            self._cache = None
            self._async_cache = None

    def __enter__(self) -> YuqueClient:
        """Enter context manager for synchronous usage."""
        self._sync_client = httpx.Client(
            base_url=BASE_URL,
            timeout=self._timeout,
            headers=self._get_headers(),
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self._close_sync_client()

    async def __aenter__(self) -> YuqueClient:
        """Enter async context manager."""
        self._async_client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=self._timeout,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self._close_async_client()

    def _get_headers(self) -> dict[str, str]:
        """Get default headers for requests."""
        return {
            "X-Auth-Token": self._token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _close_sync_client(self) -> None:
        """Close the synchronous HTTP client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def _close_async_client(self) -> None:
        """Close the asynchronous HTTP client."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def _get_sync_client(self) -> httpx.Client:
        """Get or create the synchronous HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=BASE_URL,
                timeout=self._timeout,
                headers=self._get_headers(),
            )
        return self._sync_client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create the asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=BASE_URL,
                timeout=self._timeout,
                headers=self._get_headers(),
            )
        return self._async_client

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: The HTTP response object.

        Returns:
            The JSON response data.

        Raises:
            YuqueError: Base exception for API errors.
            AuthenticationError: When authentication fails.
            PermissionDeniedError: When user lacks permission.
            NotFoundError: When resource is not found.
            InvalidArgumentError: When request arguments are invalid.
            ValidationError: When request validation fails.
            RateLimitError: When rate limit is exceeded.
            ServerError: When server returns an error.
        """
        status_code = response.status_code
        try:
            data = response.json()
        except Exception:
            data = None

        if response.is_success:
            return data if data is not None else {}

        error_messages = data.get("error", "") if isinstance(data, dict) else ""
        message = error_messages or response.text or f"HTTP {status_code} error"

        if status_code == 400:
            raise InvalidArgumentError(message, response_data=data)
        elif status_code == 401:
            raise AuthenticationError(message, response_data=data)
        elif status_code == 403:
            raise PermissionDeniedError(message, response_data=data)
        elif status_code == 404:
            raise NotFoundError(message, response_data=data)
        elif status_code == 422:
            raise ValidationError(message, response_data=data)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after else None
            raise RateLimitError(message, retry_after=retry_after_int, response_data=data)
        elif status_code >= 500:
            raise ServerError(message, status_code=status_code, response_data=data)
        else:
            raise YuqueError(message, status_code=status_code, response_data=data)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make a synchronous HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH).
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: Request body data (will be JSON encoded).

        Returns:
            Response data as a dictionary.
        """
        if method == "GET" and self._cache is not None:
            cached = self._cache.get(endpoint, params)
            if cached is not None:
                return cached

        client = self._get_sync_client()
        try:
            response = client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            result = self._handle_response(response)

            if method == "GET" and self._cache is not None:
                self._cache.set(endpoint, result, params)

            return result
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}") from e
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timeout: {e}") from e

    async def _request_async(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an asynchronous HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH).
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: Request body data (will be JSON encoded).

        Returns:
            Response data as a dictionary.
        """
        if method == "GET" and self._async_cache is not None:
            cached = await self._async_cache.get(endpoint, params)
            if cached is not None:
                return cached

        client = self._get_async_client()
        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            result = self._handle_response(response)

            if method == "GET" and self._async_cache is not None:
                await self._async_cache.set(endpoint, result, params)

            return result
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}") from e
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timeout: {e}") from e

    def _request_paginated(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Make a paginated request and return all items.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            params: Query parameters (can include 'page' and 'per_page').

        Returns:
            List of all items from all pages.
        """
        all_items: list[dict[str, Any]] = []
        page = params.get("page", 1) if params else 1

        while True:
            page_params = {**(params or {}), "page": page}
            response = self._request(method, endpoint, params=page_params)
            items = response.get("data", response if isinstance(response, list) else [])
            meta = response.get("meta")

            all_items.extend(items if isinstance(items, list) else [items])

            if meta is None:
                break

            if page >= meta.get("total_pages", page):
                break

            page += 1

        return all_items

    async def _request_paginated_async(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Async version of _request_paginated()."""
        all_items: list[dict[str, Any]] = []
        page = params.get("page", 1) if params else 1

        while True:
            page_params = {**(params or {}), "page": page}
            response = await self._request_async(method, endpoint, params=page_params)
            items = response.get("data", response if isinstance(response, list) else [])
            meta = response.get("meta")

            all_items.extend(items if isinstance(items, list) else [items])

            if meta is None:
                break

            if page >= meta.get("total_pages", page):
                break

            page += 1

        return all_items

    def _parse_paginated_response(
        self,
        response: dict[str, Any],
        data_key: str = "data",
    ) -> PaginatedResponse:
        """Parse a paginated API response."""
        from .models import PaginationMeta

        data = response.get(data_key, [])
        if not isinstance(data, list):
            data = [data]

        meta = None
        if "meta" in response:
            meta = PaginationMeta(**response["meta"])

        return PaginatedResponse(data=data, meta=meta)

    def hello(self) -> dict[str, Any]:
        """
        Test API connection.

        Returns:
            API response with hello message.

        Example:
            ```python
            client = YuqueClient(token="your-token")
            result = client.hello()
            ```
        """
        return self._request("GET", "/api/v2/hello")

    @property
    def user(self) -> UserAPI:
        """Access user-related API endpoints."""
        return UserAPI(self)

    @property
    def group(self) -> GroupAPI:
        """Access group-related API endpoints."""
        return GroupAPI(self)

    @property
    def repo(self) -> RepoAPI:
        """Access repository (book)-related API endpoints."""
        return RepoAPI(self)

    @property
    def doc(self) -> DocAPI:
        """Access document-related API endpoints."""
        return DocAPI(self)

    @property
    def search(self) -> SearchAPI:
        """Access search-related API endpoints."""
        return SearchAPI(self)
