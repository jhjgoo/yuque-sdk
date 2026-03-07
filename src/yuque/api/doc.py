"""Document API endpoints."""

from __future__ import annotations

from typing import Any

from ..models import PaginatedResponse
from .base import BaseAPI


class DocAPI(BaseAPI):
    """API endpoints for document operations."""

    def get(self, doc_id: int) -> dict[str, Any]:
        """Get a document by ID."""
        response = self._request("GET", f"/api/v2/repos/docs/{doc_id}")
        return response["data"]

    async def get_async(self, doc_id: int) -> dict[str, Any]:
        """Async version of get()."""
        response = await self._request_async("GET", f"/api/v2/repos/docs/{doc_id}")
        return response["data"]

    def get_by_repo(self, book_id: int, offset: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get documents in a repository."""
        response = self._request(
            "GET",
            f"/api/v2/repos/{book_id}/docs",
            params={"offset": offset, "limit": limit},
        )
        return self._parse_paginated_response(response)

    async def get_by_repo_async(
        self, book_id: int, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_by_repo()."""
        response = await self._request_async(
            "GET",
            f"/api/v2/repos/{book_id}/docs",
            params={"offset": offset, "limit": limit},
        )
        return self._parse_paginated_response(response)

    def get_by_path(
        self, group_login: str, book_slug: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Get documents by group path and book slug."""
        response = self._request(
            "GET",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            params={"offset": offset, "limit": limit},
        )
        return self._parse_paginated_response(response)

    async def get_by_path_async(
        self, group_login: str, book_slug: str, offset: int = 0, limit: int = 100
    ) -> PaginatedResponse:
        """Async version of get_by_path()."""
        response = await self._request_async(
            "GET",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            params={"offset": offset, "limit": limit},
        )
        return self._parse_paginated_response(response)

    def create(
        self,
        book_id: int,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new document."""
        response = self._request(
            "POST",
            f"/api/v2/repos/{book_id}/docs",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    async def create_async(
        self,
        book_id: int,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Async version of create()."""
        response = await self._request_async(
            "POST",
            f"/api/v2/repos/{book_id}/docs",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    def create_by_path(
        self,
        group_login: str,
        book_slug: str,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new document by group path and book slug."""
        response = self._request(
            "POST",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    async def create_by_path_async(
        self,
        group_login: str,
        book_slug: str,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Async version of create_by_path()."""
        response = await self._request_async(
            "POST",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    def update(
        self,
        book_id: int,
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update an existing document."""
        response = self._request(
            "PUT",
            f"/api/v2/repos/{book_id}/docs/{doc_id}",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    async def update_async(
        self,
        book_id: int,
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Async version of update()."""
        response = await self._request_async(
            "PUT",
            f"/api/v2/repos/{book_id}/docs/{doc_id}",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    def update_by_repo(
        self,
        book_id: int,
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update a document in a repository."""
        response = self._request(
            "PUT",
            f"/api/v2/repos/{book_id}/docs/{doc_id}",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    async def update_by_repo_async(
        self,
        book_id: int,
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Async version of update_by_repo()."""
        response = await self._request_async(
            "PUT",
            f"/api/v2/repos/{book_id}/docs/{doc_id}",
            json_data={
                "title": title,
                "slug": slug,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    def delete(self, book_id: int, doc_id: int) -> dict[str, Any]:
        """Delete a document."""
        response = self._request("DELETE", f"/api/v2/repos/{book_id}/docs/{doc_id}")
        return response.get("data", {})

    async def delete_async(self, book_id: int, doc_id: int) -> dict[str, Any]:
        """Async version of delete()."""
        response = await self._request_async("DELETE", f"/api/v2/repos/{book_id}/docs/{doc_id}")
        return response.get("data", {})

    def get_version(self, version_id: int) -> dict[str, Any]:
        """Get a document version."""
        response = self._request("GET", f"/api/v2/doc_versions/{version_id}")
        return response["data"]

    async def get_version_async(self, version_id: int) -> dict[str, Any]:
        """Async version of get_version()."""
        response = await self._request_async("GET", f"/api/v2/doc_versions/{version_id}")
        return response["data"]

    def get_doc_by_path(self, namespace: str, slug: str, raw: bool = False) -> dict[str, Any]:
        """Get a single document by namespace and slug.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.
            raw: If True, return raw content without rendering.

        Returns:
            Document information dictionary.

        Example:
            >>> doc = client.doc.get_doc_by_path("my-group/my-book", "intro")
            >>> print(doc["title"])
        """
        params = {"raw": 1} if raw else None
        response = self._request("GET", f"/api/v2/repos/{namespace}/docs/{slug}", params=params)
        return response["data"]

    async def get_doc_by_path_async(
        self, namespace: str, slug: str, raw: bool = False
    ) -> dict[str, Any]:
        """Get a single document by namespace and slug asynchronously.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.
            raw: If True, return raw content without rendering.

        Returns:
            Document information dictionary.

        Example:
            >>> doc = await client.doc.get_doc_by_path_async("my-group/my-book", "intro")
            >>> print(doc["title"])
        """
        params = {"raw": 1} if raw else None
        response = await self._request_async(
            "GET", f"/api/v2/repos/{namespace}/docs/{slug}", params=params
        )
        return response["data"]

    def update_by_path(
        self,
        namespace: str,
        slug: str,
        title: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update a document by namespace and slug.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.
            title: New document title.
            body: New document body content.
            format: Document format (default: "markdown").
            public: Visibility setting (0=private, 1=public).

        Returns:
            Updated document information dictionary.

        Example:
            >>> doc = client.doc.update_by_path(
            ...     "my-group/my-book",
            ...     "intro",
            ...     title="Updated Title",
            ...     body="New content"
            ... )
        """
        response = self._request(
            "PUT",
            f"/api/v2/repos/{namespace}/docs/{slug}",
            json_data={
                "title": title,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    async def update_by_path_async(
        self,
        namespace: str,
        slug: str,
        title: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update a document by namespace and slug asynchronously.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.
            title: New document title.
            body: New document body content.
            format: Document format (default: "markdown").
            public: Visibility setting (0=private, 1=public).

        Returns:
            Updated document information dictionary.

        Example:
            >>> doc = await client.doc.update_by_path_async(
            ...     "my-group/my-book",
            ...     "intro",
            ...     title="Updated Title",
            ...     body="New content"
            ... )
        """
        response = await self._request_async(
            "PUT",
            f"/api/v2/repos/{namespace}/docs/{slug}",
            json_data={
                "title": title,
                "body": body,
                "format": format,
                "public": public,
            },
        )
        return response["data"]

    def delete_by_path(self, namespace: str, slug: str) -> dict[str, Any]:
        """Delete a document by namespace and slug.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.

        Returns:
            Deletion result dictionary.

        Example:
            >>> result = client.doc.delete_by_path("my-group/my-book", "old-doc")
        """
        response = self._request("DELETE", f"/api/v2/repos/{namespace}/docs/{slug}")
        return response.get("data", {})

    async def delete_by_path_async(self, namespace: str, slug: str) -> dict[str, Any]:
        """Delete a document by namespace and slug asynchronously.

        Args:
            namespace: The namespace in format "group_login/book_slug".
            slug: The document slug.

        Returns:
            Deletion result dictionary.

        Example:
            >>> result = await client.doc.delete_by_path_async("my-group/my-book", "old-doc")
        """
        response = await self._request_async("DELETE", f"/api/v2/repos/{namespace}/docs/{slug}")
        return response.get("data", {})
