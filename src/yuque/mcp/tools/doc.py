"""Document-related MCP tools for Yuque API.

This module provides MCP tools for document operations in Yuque:
- Get document by ID
- Get documents by repository
- Get documents by path
- Create document
- Create document by path
- Update document
- Update document by repository
- Delete document
- Get document version
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ...client import YuqueClient


def register_doc_tools(mcp: FastMCP, client: YuqueClient) -> None:
    """Register all document-related MCP tools with the server.

    This function registers the following tools:
    - yuque_get_doc: Get document by ID
    - yuque_get_docs_by_repo: Get documents in a repository
    - yuque_get_docs_by_path: Get documents by group and book path
    - yuque_create_doc: Create a new document
    - yuque_create_doc_by_path: Create document by path
    - yuque_update_doc: Update an existing document
    - yuque_update_doc_by_repo: Update document in a repository
    - yuque_delete_doc: Delete a document
    - yuque_get_doc_version: Get a specific document version

    Args:
        mcp: The FastMCP server instance to register tools with.
        client: Authenticated YuqueClient instance.

    Example:
        ```python
        from mcp.server.fastmcp import FastMCP
        from yuque import YuqueClient
        from yuque.mcp.tools.doc import register_doc_tools

        mcp = FastMCP("yuque-mcp")
        client = YuqueClient(token="your-token")
        register_doc_tools(mcp, client)
        ```
    """

    @mcp.tool()
    async def yuque_get_doc(doc_id: int) -> dict[str, Any]:
        """Get detailed information about a specific document by its ID.

        This tool retrieves comprehensive information about a document including
        its title, content, metadata, version information, and statistics.

        Args:
            doc_id: The unique identifier of the document to retrieve.

        Returns:
            Document details including:
            - Document ID, slug, and title
            - Body content and format
            - Creator and editor information
            - Repository (book) information
            - Public level and statistics (reads, likes, comments)
            - Version information
            - Creation and update timestamps

        Example:
            To get document with ID 12345:
            {
                "doc_id": 12345
            }
        """
        try:
            doc = client.doc.get(doc_id=doc_id)
            return {
                "success": True,
                "data": _format_doc(doc),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get document {doc_id}",
            }

    @mcp.tool()
    async def yuque_get_docs_by_repo(
        book_id: int, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        """Get all documents in a specific repository (knowledge base).

        This tool retrieves a paginated list of documents within a repository,
        useful for exploring all documents in a knowledge base.

        Args:
            book_id: The unique identifier of the repository (knowledge base).
            offset: Number of items to skip for pagination (default: 0).
            limit: Maximum number of items to return (default: 100, max: 100).

        Returns:
            List of documents with pagination metadata including:
            - Document ID, slug, and title
            - Creator information
            - Read count and statistics
            - Creation and update timestamps

        Example:
            To get the first 20 documents in repository 12345:
            {
                "book_id": 12345,
                "offset": 0,
                "limit": 20
            }
        """
        try:
            limit = min(limit, 100)
            result = client.doc.get_by_repo(book_id=book_id, offset=offset, limit=limit)

            docs = [_format_doc_summary(doc) for doc in result.data]

            return {
                "success": True,
                "data": {
                    "book_id": book_id,
                    "documents": docs,
                    "total": result.meta.total if result.meta else len(docs),
                    "offset": offset,
                    "limit": limit,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get documents for repository {book_id}",
            }

    @mcp.tool()
    async def yuque_get_docs_by_path(
        group_login: str, book_slug: str, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        """Get documents using group login and book slug path.

        This is useful when you know the repository's path but not its ID.
        The path format is: /groups/{group_login}/{book_slug}

        Args:
            group_login: The login name of the group (e.g., "my-team").
            book_slug: The slug identifier of the repository (e.g., "api-docs").
            offset: Number of items to skip for pagination (default: 0).
            limit: Maximum number of items to return (default: 100, max: 100).

        Returns:
            List of documents with pagination metadata.

        Example:
            To get documents from "api-docs" in group "engineering":
            {
                "group_login": "engineering",
                "book_slug": "api-docs",
                "offset": 0,
                "limit": 20
            }
        """
        try:
            limit = min(limit, 100)
            result = client.doc.get_by_path(
                group_login=group_login, book_slug=book_slug, offset=offset, limit=limit
            )

            docs = [_format_doc_summary(doc) for doc in result.data]

            return {
                "success": True,
                "data": {
                    "path": f"{group_login}/{book_slug}",
                    "documents": docs,
                    "total": result.meta.total if result.meta else len(docs),
                    "offset": offset,
                    "limit": limit,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get documents for {group_login}/{book_slug}",
            }

    @mcp.tool()
    async def yuque_create_doc(
        book_id: int,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new document in a repository.

        This tool creates a new document in the specified repository with the
        provided content and settings.

        Args:
            book_id: The unique identifier of the repository (knowledge base).
            title: The title of the document (default: "无标题").
            slug: The URL slug for the document. If not provided, one will be
                generated automatically.
            body: The content of the document. Can be markdown, HTML, or lake format.
            format: The format of the body content (default: "markdown").
                Options: "markdown", "html", "lake".
            public: The visibility level of the document (default: 0).
                - 0: Private (only accessible to repository members)
                - 1: Public (accessible to everyone)
                - 2: Enterprise-wide (accessible within organization)

        Returns:
            Created document details including:
            - Document ID and slug
            - Title and initial content
            - Creator information
            - Creation timestamp

        Example:
            To create a new markdown document:
            {
                "book_id": 12345,
                "title": "My New Document",
                "body": "# Hello World\\n\\nThis is my first document.",
                "format": "markdown",
                "public": 0
            }
        """
        try:
            doc = client.doc.create(
                book_id=book_id,
                title=title,
                slug=slug,
                body=body,
                format=format,
                public=public,
            )
            return {
                "success": True,
                "data": _format_doc(doc),
                "message": f"Document '{title}' created successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create document in repository {book_id}",
            }

    @mcp.tool()
    async def yuque_create_doc_by_path(
        group_login: str,
        book_slug: str,
        title: str = "无标题",
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Create a new document using group and book path.

        This is useful when you know the repository's path but not its ID.
        The path format is: /groups/{group_login}/{book_slug}

        Args:
            group_login: The login name of the group (e.g., "my-team").
            book_slug: The slug identifier of the repository (e.g., "api-docs").
            title: The title of the document (default: "无标题").
            slug: The URL slug for the document.
            body: The content of the document.
            format: The format of the body content (default: "markdown").
            public: The visibility level (default: 0).

        Returns:
            Created document details.

        Example:
            To create a document in "engineering/api-docs":
            {
                "group_login": "engineering",
                "book_slug": "api-docs",
                "title": "API Reference",
                "body": "# API Reference\\n\\n## Overview",
                "format": "markdown",
                "public": 1
            }
        """
        try:
            doc = client.doc.create_by_path(
                group_login=group_login,
                book_slug=book_slug,
                title=title,
                slug=slug,
                body=body,
                format=format,
                public=public,
            )
            return {
                "success": True,
                "data": _format_doc(doc),
                "message": f"Document '{title}' created successfully at {group_login}/{book_slug}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create document at {group_login}/{book_slug}",
            }

    @mcp.tool()
    async def yuque_update_doc(
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update an existing document.

        This tool updates the content and settings of an existing document.
        Only provided parameters will be updated; others remain unchanged.

        Args:
            doc_id: The unique identifier of the document to update.
            title: The new title for the document (optional).
            slug: The new URL slug for the document (optional).
            body: The new content for the document (optional).
            format: The format of the body content (default: "markdown").
            public: The visibility level (default: 0).

        Returns:
            Updated document details including:
            - Document ID and new slug/title
            - Updated content
            - New version number
            - Update timestamp

        Example:
            To update a document's title and content:
            {
                "doc_id": 12345,
                "title": "Updated Title",
                "body": "# Updated Content\\n\\nThis document has been updated.",
                "format": "markdown",
                "public": 1
            }
        """
        try:
            doc = client.doc.update(
                doc_id=doc_id,
                title=title,
                slug=slug,
                body=body,
                format=format,
                public=public,
            )
            return {
                "success": True,
                "data": _format_doc(doc),
                "message": f"Document {doc_id} updated successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update document {doc_id}",
            }

    @mcp.tool()
    async def yuque_update_doc_by_repo(
        book_id: int,
        doc_id: int,
        title: str | None = None,
        slug: str | None = None,
        body: str | None = None,
        format: str = "markdown",
        public: int = 0,
    ) -> dict[str, Any]:
        """Update a document within a specific repository.

        This tool updates a document while explicitly specifying the repository,
        providing additional context for the update operation.

        Args:
            book_id: The unique identifier of the repository.
            doc_id: The unique identifier of the document to update.
            title: The new title for the document (optional).
            slug: The new URL slug for the document (optional).
            body: The new content for the document (optional).
            format: The format of the body content (default: "markdown").
            public: The visibility level (default: 0).

        Returns:
            Updated document details.

        Example:
            To update a document in repository 12345:
            {
                "book_id": 12345,
                "doc_id": 67890,
                "title": "Updated Title",
                "body": "Updated content here..."
            }
        """
        try:
            doc = client.doc.update_by_repo(
                book_id=book_id,
                doc_id=doc_id,
                title=title,
                slug=slug,
                body=body,
                format=format,
                public=public,
            )
            return {
                "success": True,
                "data": _format_doc(doc),
                "message": f"Document {doc_id} in repository {book_id} updated successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update document {doc_id} in repository {book_id}",
            }

    @mcp.tool()
    async def yuque_delete_doc(doc_id: int) -> dict[str, Any]:
        """Delete a document.

        This tool permanently deletes a document from the repository.
        This action cannot be undone, so use with caution.

        Args:
            doc_id: The unique identifier of the document to delete.

        Returns:
            Confirmation of deletion including:
            - Document ID that was deleted
            - Success status

        Warning:
            This action is permanent and cannot be undone.

        Example:
            To delete document with ID 12345:
            {
                "doc_id": 12345
            }
        """
        try:
            client.doc.delete(doc_id=doc_id)
            return {
                "success": True,
                "data": {
                    "doc_id": doc_id,
                    "deleted": True,
                },
                "message": f"Document {doc_id} deleted successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete document {doc_id}",
            }

    @mcp.tool()
    async def yuque_get_doc_version(version_id: int) -> dict[str, Any]:
        """Get a specific version of a document.

        This tool retrieves a historical version of a document, allowing you to
        view previous versions or compare changes over time.

        Args:
            version_id: The unique identifier of the document version to retrieve.

        Returns:
            Document version details including:
            - Version ID and document ID
            - Version content
            - Version description/commit message
            - Creation timestamp

        Example:
            To get version 42 of a document:
            {
                "version_id": 42
            }
        """
        try:
            version = client.doc.get_version(version_id=version_id)
            return {
                "success": True,
                "data": _format_doc_version(version),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get document version {version_id}",
            }


def _format_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Format document data for better readability.

    Args:
        doc: Raw document data from API.

    Returns:
        Formatted document dictionary.
    """
    formatted: dict[str, Any] = {
        "id": doc.get("id"),
        "slug": doc.get("slug"),
        "title": doc.get("title"),
        "body": doc.get("body"),
        "body_format": _get_format_label(doc.get("body_format", 1)),
        "creator_id": doc.get("creator_id"),
        "user_id": doc.get("user_id"),
        "book_id": doc.get("book_id"),
        "public": _get_public_label(doc.get("public", 0)),
        "version": doc.get("version"),
        "read_count": doc.get("read_count", 0),
        "likes_count": doc.get("likes_count", 0),
        "comments_count": doc.get("comments_count", 0),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
        "published_at": doc.get("published_at"),
    }

    # Add user information if available
    if doc.get("user"):
        formatted["creator"] = {
            "name": doc["user"].get("name"),
            "login": doc["user"].get("login"),
        }

    # Add book information if available
    if doc.get("book"):
        formatted["repository"] = {
            "name": doc["book"].get("name"),
            "slug": doc["book"].get("slug"),
        }

    # Add optional fields
    if draft_version := doc.get("draft_version"):
        formatted["draft_version"] = draft_version

    if last_editor_id := doc.get("last_editor_id"):
        formatted["last_editor_id"] = last_editor_id

    if word_count := doc.get("word_count"):
        formatted["word_count"] = word_count

    if cover := doc.get("cover"):
        formatted["cover"] = cover

    return formatted


def _format_doc_summary(doc: dict[str, Any]) -> dict[str, Any]:
    """Format document summary for list views (without full body content).

    Args:
        doc: Raw document data from API.

    Returns:
        Formatted document summary dictionary.
    """
    formatted: dict[str, Any] = {
        "id": doc.get("id"),
        "slug": doc.get("slug"),
        "title": doc.get("title"),
        "creator_id": doc.get("creator_id"),
        "book_id": doc.get("book_id"),
        "public": _get_public_label(doc.get("public", 0)),
        "read_count": doc.get("read_count", 0),
        "likes_count": doc.get("likes_count", 0),
        "comments_count": doc.get("comments_count", 0),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

    # Add user information if available
    if doc.get("user"):
        formatted["creator"] = {
            "name": doc["user"].get("name"),
            "login": doc["user"].get("login"),
        }

    return formatted


def _format_doc_version(version: dict[str, Any]) -> dict[str, Any]:
    """Format document version data.

    Args:
        version: Raw version data from API.

    Returns:
        Formatted version dictionary.
    """
    formatted: dict[str, Any] = {
        "id": version.get("id"),
        "document_id": version.get("document_id"),
        "content": version.get("content"),
        "created_at": version.get("created_at"),
    }

    # Add optional description
    if description := version.get("description"):
        formatted["description"] = description

    return formatted


def _get_public_label(public_level: int) -> str:
    """Convert public level to human-readable label.

    Args:
        public_level: Numeric public level.

    Returns:
        Human-readable label string.
    """
    labels = {
        0: "private",
        1: "public",
        2: "enterprise-wide",
    }
    return labels.get(public_level, f"unknown ({public_level})")


def _get_format_label(body_format: int) -> str:
    """Convert body format code to human-readable label.

    Args:
        body_format: Numeric format code.

    Returns:
        Human-readable format string.
    """
    formats = {
        1: "markdown",
        2: "html",
        3: "lake",
    }
    return formats.get(body_format, f"unknown ({body_format})")
