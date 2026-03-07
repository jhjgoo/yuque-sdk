"""Repository (Book) API endpoints."""

from __future__ import annotations

from typing import Any

from ..models import PaginatedResponse
from .base import BaseAPI


class RepoAPI(BaseAPI):
    """API endpoints for repository (knowledge base) operations."""

    def get(self, book_id: int) -> dict[str, Any]:
        """Get a repository by ID."""
        response = self._request("GET", f"/api/v2/repos/{book_id}")
        return response["data"]

    async def get_async(self, book_id: int) -> dict[str, Any]:
        """Async version of get()."""
        response = await self._request_async("GET", f"/api/v2/repos/{book_id}")
        return response["data"]

    def get_by_path(self, group_login: str, book_slug: str) -> dict[str, Any]:
        """Get a repository by group path and book slug."""
        response = self._request("GET", f"/api/v2/repos/{group_login}/{book_slug}")
        return response["data"]

    async def get_by_path_async(self, group_login: str, book_slug: str) -> dict[str, Any]:
        """Async version of get_by_path()."""
        response = await self._request_async("GET", f"/api/v2/repos/{group_login}/{book_slug}")
        return response["data"]

    def list(self, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """List repositories for the authenticated user."""
        user = self._client.user.get_me()
        login = user.login if hasattr(user, "login") else user.data.get("login")
        response = self._request(
            "GET", f"/api/v2/users/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def list_async(self, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Async version of list()."""
        user = await self._client.user.get_me_async()
        login = user.login if hasattr(user, "login") else user.data.get("login")
        response = await self._request_async(
            "GET", f"/api/v2/users/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def list_async(self, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Async version of list()."""
        response = await self._request_async(
            "GET", "/api/v2/user/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    def get_user_repos(self, login: str, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get repositories for a specific user."""
        response = self._request(
            "GET", f"/api/v2/users/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def get_user_repos_async(
        self, login: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_user_repos()."""
        response = await self._request_async(
            "GET", f"/api/v2/users/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    def get_group_repos(self, login: str, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get repositories in a group."""
        response = self._request(
            "GET", f"/api/v2/groups/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    async def get_group_repos_async(
        self, login: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_group_repos()."""
        response = await self._request_async(
            "GET", f"/api/v2/groups/{login}/repos", params={"offset": offset, "limit": limit}
        )
        return self._parse_paginated_response(response)

    def get_toc(self, book_id: int) -> list[dict[str, Any]]:
        """Get table of contents for a repository."""
        response = self._request("GET", f"/api/v2/repos/{book_id}/toc")
        return response.get("data", [])

    async def get_toc_async(self, book_id: int) -> list[dict[str, Any]]:
        """Async version of get_toc()."""
        response = await self._request_async("GET", f"/api/v2/repos/{book_id}/toc")
        return response.get("data", [])

    def get_toc_by_path(self, group_login: str, book_slug: str) -> list[dict[str, Any]]:
        """Get table of contents by group path and book slug."""
        response = self._request("GET", f"/api/v2/repos/{group_login}/{book_slug}/toc")
        return response.get("data", [])

    async def get_toc_by_path_async(self, group_login: str, book_slug: str) -> list[dict[str, Any]]:
        """Async version of get_toc_by_path()."""
        response = await self._request_async("GET", f"/api/v2/repos/{group_login}/{book_slug}/toc")
        return response.get("data", [])

    def create_repo(
        self,
        owner_login: str,
        owner_type: str,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new repository (knowledge base).

        Args:
            owner_login: The login name of the owner (user or group).
            owner_type: The type of owner, either "User" or "Group".
            name: The name of the repository.
            slug: The URL slug for the repository (optional, auto-generated if not provided).
            description: The description of the repository.
            public: Visibility setting (0=private, 1=public, 2=public to internet).

        Returns:
            The created repository information.
        """
        response = self._request(
            "POST",
            "/api/v2/repos",
            json_data={
                "owner_login": owner_login,
                "owner_type": owner_type,
                "name": name,
                "slug": slug,
                "description": description,
                "public": public,
            },
        )
        return response["data"]

    async def create_repo_async(
        self,
        owner_login: str,
        owner_type: str,
        name: str,
        slug: str | None = None,
        description: str | None = None,
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new repository (knowledge base) asynchronously.

        Args:
            owner_login: The login name of the owner (user or group).
            owner_type: The type of owner, either "User" or "Group".
            name: The name of the repository.
            slug: The URL slug for the repository (optional, auto-generated if not provided).
            description: The description of the repository.
            public: Visibility setting (0=private, 1=public, 2=public to internet).

        Returns:
            The created repository information.
        """
        response = await self._request_async(
            "POST",
            "/api/v2/repos",
            json_data={
                "owner_login": owner_login,
                "owner_type": owner_type,
                "name": name,
                "slug": slug,
                "description": description,
                "public": public,
            },
        )
        return response["data"]

    def update_repo(
        self,
        book_id: int,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        public: int | None = None,
        toc: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update an existing repository (knowledge base).

        Args:
            book_id: The ID of the repository to update.
            name: New name for the repository.
            slug: New URL slug for the repository.
            description: New description for the repository.
            public: New visibility setting (0=private, 1=public, 2=public to internet).
            toc: New table of contents structure.

        Returns:
            The updated repository information.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if slug is not None:
            data["slug"] = slug
        if description is not None:
            data["description"] = description
        if public is not None:
            data["public"] = public
        if toc is not None:
            data["toc"] = toc

        response = self._request("PUT", f"/api/v2/repos/{book_id}", json_data=data)
        return response["data"]

    async def update_repo_async(
        self,
        book_id: int,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        public: int | None = None,
        toc: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update an existing repository (knowledge base) asynchronously.

        Args:
            book_id: The ID of the repository to update.
            name: New name for the repository.
            slug: New URL slug for the repository.
            description: New description for the repository.
            public: New visibility setting (0=private, 1=public, 2=public to internet).
            toc: New table of contents structure.

        Returns:
            The updated repository information.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if slug is not None:
            data["slug"] = slug
        if description is not None:
            data["description"] = description
        if public is not None:
            data["public"] = public
        if toc is not None:
            data["toc"] = toc

        response = await self._request_async("PUT", f"/api/v2/repos/{book_id}", json_data=data)
        return response["data"]

    def delete_repo(self, book_id: int) -> dict[str, Any]:
        """Delete a repository (knowledge base).

        Args:
            book_id: The ID of the repository to delete.

        Returns:
            Deletion result dictionary.
        """
        response = self._request("DELETE", f"/api/v2/repos/{book_id}")
        return response.get("data", {})

    async def delete_repo_async(self, book_id: int) -> dict[str, Any]:
        """Delete a repository (knowledge base) asynchronously.

        Args:
            book_id: The ID of the repository to delete.

        Returns:
            Deletion result dictionary.
        """
        response = await self._request_async("DELETE", f"/api/v2/repos/{book_id}")
        return response.get("data", {})
