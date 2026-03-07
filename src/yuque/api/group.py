"""Group API endpoints."""

from __future__ import annotations

from typing import Any

from ..models import PaginatedResponse
from .base import BaseAPI


class GroupAPI(BaseAPI):
    """API endpoints for group operations."""

    def get(self, login: str) -> dict[str, Any]:
        """Get a group by login name.

        DEPRECATED: The Yuque API does not have a direct endpoint to get group info.
        This method will always return a 404 error.
        Consider using get_members() or get_repos() to get group information.
        """
        response = self._request("GET", f"/api/v2/groups/{login}")
        return response["data"]

    async def get_async(self, login: str) -> dict[str, Any]:
        """Async version of get()."""
        response = await self._request_async("GET", f"/api/v2/groups/{login}")
        return response["data"]

    def get_repos(self, login: str, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get repositories in a group."""
        response = self._request(
            "GET", f"/api/v2/groups/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def get_repos_async(
        self, login: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_repos()."""
        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    def get_members(self, login: str, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get members of a group."""
        response = self._request(
            "GET", f"/api/v2/groups/{login}/users", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def get_members_async(
        self, login: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_members()."""
        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/users", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    def add_member(self, login: str, user_id: int, role: int = 1) -> dict[str, Any]:
        """Add a member to a group."""
        response = self._request(
            "POST",
            f"/api/v2/groups/{login}/users",
            json_data={"user_id": user_id, "role": role},
        )
        return response.get("data", {})

    async def add_member_async(self, login: str, user_id: int, role: int = 1) -> dict[str, Any]:
        """Async version of add_member()."""
        response = await self._request_async(
            "POST",
            f"/api/v2/groups/{login}/users",
            json_data={"user_id": user_id, "role": role},
        )
        return response.get("data", {})

    def update_member(self, login: str, user_id: int, role: int) -> dict[str, Any]:
        """Update a member's role in a group."""
        response = self._request(
            "PUT",
            f"/api/v2/groups/{login}/users/{user_id}",
            json_data={"role": role},
        )
        return response.get("data", {})

    async def update_member_async(self, login: str, user_id: int, role: int) -> dict[str, Any]:
        """Async version of update_member()."""
        response = await self._request_async(
            "PUT",
            f"/api/v2/groups/{login}/users/{user_id}",
            json_data={"role": role},
        )
        return response.get("data", {})

    def remove_member(self, login: str, user_id: int) -> dict[str, Any]:
        """Remove a member from a group."""
        response = self._request("DELETE", f"/api/v2/groups/{login}/users/{user_id}")
        return response.get("data", {})

    async def remove_member_async(self, login: str, user_id: int) -> dict[str, Any]:
        """Async version of remove_member()."""
        response = await self._request_async("DELETE", f"/api/v2/groups/{login}/users/{user_id}")
        return response.get("data", {})

    def get_statistics(self, login: str) -> dict[str, Any]:
        """Get group statistics."""
        response = self._request("GET", f"/api/v2/groups/{login}/statistics")
        return response["data"]

    async def get_statistics_async(self, login: str) -> dict[str, Any]:
        """Async version of get_statistics()."""
        response = await self._request_async("GET", f"/api/v2/groups/{login}/statistics")
        return response["data"]

    def get_by_id(self, group_id: int) -> dict[str, Any]:
        """Get a group by ID.

        Args:
            group_id: The unique identifier of the group.

        Returns:
            Group information dictionary.

        Example:
            >>> group = client.group.get_by_id(12345)
            >>> print(group["name"])
        """
        response = self._request("GET", f"/api/v2/groups/{group_id}")
        return response["data"]

    async def get_by_id_async(self, group_id: int) -> dict[str, Any]:
        """Get a group by ID asynchronously.

        Args:
            group_id: The unique identifier of the group.

        Returns:
            Group information dictionary.

        Example:
            >>> group = await client.group.get_by_id_async(12345)
            >>> print(group["name"])
        """
        response = await self._request_async("GET", f"/api/v2/groups/{group_id}")
        return response["data"]

    def get_member_stats(
        self,
        login: str,
        name: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
        sortField: str | None = None,
        sortOrder: str | None = None,
    ) -> PaginatedResponse:
        """Get member statistics for a group.

        Args:
            login: Group login name.
            name: Filter by member name.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).
            sortField: Field to sort by (e.g., "created_at", "updated_at").
            sortOrder: Sort order ("asc" or "desc").

        Returns:
            Paginated response with member statistics.

        Example:
            >>> stats = client.group.get_member_stats("my-group", range="30d")
            >>> for member in stats.data:
            ...     print(member["name"], member["docs_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if name:
            params["name"] = name
        if range:
            params["range"] = range
        if sortField:
            params["sortField"] = sortField
        if sortOrder:
            params["sortOrder"] = sortOrder

        response = self._request("GET", f"/api/v2/groups/{login}/stats/members", params=params)
        return self._parse_paginated_response(response)

    async def get_member_stats_async(
        self,
        login: str,
        name: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
        sortField: str | None = None,
        sortOrder: str | None = None,
    ) -> PaginatedResponse:
        """Get member statistics for a group asynchronously.

        Args:
            login: Group login name.
            name: Filter by member name.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).
            sortField: Field to sort by (e.g., "created_at", "updated_at").
            sortOrder: Sort order ("asc" or "desc").

        Returns:
            Paginated response with member statistics.

        Example:
            >>> stats = await client.group.get_member_stats_async("my-group", range="30d")
            >>> for member in stats.data:
            ...     print(member["name"], member["docs_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if name:
            params["name"] = name
        if range:
            params["range"] = range
        if sortField:
            params["sortField"] = sortField
        if sortOrder:
            params["sortOrder"] = sortOrder

        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/stats/members", params=params
        )
        return self._parse_paginated_response(response)

    def get_book_stats(
        self,
        login: str,
        name: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Get book (knowledge base) statistics for a group.

        Args:
            login: Group login name.
            name: Filter by book name.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).

        Returns:
            Paginated response with book statistics.

        Example:
            >>> stats = client.group.get_book_stats("my-group", range="30d")
            >>> for book in stats.data:
            ...     print(book["name"], book["docs_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if name:
            params["name"] = name
        if range:
            params["range"] = range

        response = self._request("GET", f"/api/v2/groups/{login}/stats/books", params=params)
        return self._parse_paginated_response(response)

    async def get_book_stats_async(
        self,
        login: str,
        name: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Get book (knowledge base) statistics for a group asynchronously.

        Args:
            login: Group login name.
            name: Filter by book name.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).

        Returns:
            Paginated response with book statistics.

        Example:
            >>> stats = await client.group.get_book_stats_async("my-group", range="30d")
            >>> for book in stats.data:
            ...     print(book["name"], book["docs_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if name:
            params["name"] = name
        if range:
            params["range"] = range

        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/stats/books", params=params
        )
        return self._parse_paginated_response(response)

    def get_doc_stats(
        self,
        login: str,
        title: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Get document statistics for a group.

        Args:
            login: Group login name.
            title: Filter by document title.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).

        Returns:
            Paginated response with document statistics.

        Example:
            >>> stats = client.group.get_doc_stats("my-group", range="30d")
            >>> for doc in stats.data:
            ...     print(doc["title"], doc["read_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if title:
            params["title"] = title
        if range:
            params["range"] = range

        response = self._request("GET", f"/api/v2/groups/{login}/stats/docs", params=params)
        return self._parse_paginated_response(response)

    async def get_doc_stats_async(
        self,
        login: str,
        title: str | None = None,
        range: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Get document statistics for a group asynchronously.

        Args:
            login: Group login name.
            title: Filter by document title.
            range: Time range filter (e.g., "7d", "30d", "90d").
            page: Page number (default: 1).
            limit: Items per page (default: 20).

        Returns:
            Paginated response with document statistics.

        Example:
            >>> stats = await client.group.get_doc_stats_async("my-group", range="30d")
            >>> for doc in stats.data:
            ...     print(doc["title"], doc["read_count"])
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if title:
            params["title"] = title
        if range:
            params["range"] = range

        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/stats/docs", params=params
        )
        return self._parse_paginated_response(response)
