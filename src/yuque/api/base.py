"""Base API class and utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from ..exceptions import (
    AuthenticationError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
    YuqueError,
)
from ..models import PaginatedResponse, PaginationMeta

if TYPE_CHECKING:
    from ..client import YuqueClient


BASE_URL = "https://www.yuque.com"


class BaseAPI:
    """Base class for all API endpoints."""

    def __init__(self, client: YuqueClient) -> None:
        self._client = client

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
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
        """Make a synchronous HTTP request."""
        return self._client._request(method, endpoint, params, json_data)

    async def _request_async(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an asynchronous HTTP request."""
        return await self._client._request_async(method, endpoint, params, json_data)

    def _parse_paginated_response(
        self,
        response: dict[str, Any],
        data_key: str = "data",
    ) -> PaginatedResponse:
        """Parse a paginated API response."""
        data = response.get(data_key, [])
        if not isinstance(data, list):
            data = [data]

        meta = None
        if "meta" in response:
            meta = PaginationMeta(**response["meta"])

        return PaginatedResponse(data=data, meta=meta)
