"""Search API endpoints."""

from __future__ import annotations

from typing import Any

from ..models import PaginatedResponse
from .base import BaseAPI


class SearchAPI(BaseAPI):
    """API endpoints for search operations."""

    def search(
        self,
        keyword: str,
        type: str = "doc",
        page: int = 1,
    ) -> PaginatedResponse:
        """Search across Yuque."""
        params: dict[str, Any] = {
            "q": keyword,
            "type": type,
            "page": page,
        }

        response = self._request("GET", "/api/v2/search", params=params)
        return self._parse_paginated_response(response)

    async def search_async(
        self,
        keyword: str,
        type: str = "doc",
        page: int = 1,
    ) -> PaginatedResponse:
        """Search across Yuque asynchronously."""
        params: dict[str, Any] = {
            "q": keyword,
            "type": type,
            "page": page,
        }

        response = await self._request_async("GET", "/api/v2/search", params=params)
        return self._parse_paginated_response(response)
