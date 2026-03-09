"""Repository (Knowledge Base) MCP tools for Yuque API.

Provides MCP tools for repository operations including:
- Getting repository details
- Listing repositories
- Managing table of contents
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from ...client import YuqueClient


def register_repo_tools(mcp: FastMCP, client: YuqueClient) -> None:
    """Register all repository-related MCP tools.

    Args:
        mcp: The FastMCP server instance.
        client: The Yuque API client instance.
    """

    @mcp.tool()
    async def yuque_get_repo(book_id: int) -> dict[str, Any]:
        """Get detailed information about a specific repository (knowledge base).

        Args:
            book_id: The unique identifier of the repository.

        Returns:
            Repository details including name, description, creator, and settings.

        Example:
            To get repository with ID 12345:
            {
                "book_id": 12345
            }
        """
        try:
            repo = client.repo.get(book_id=book_id)
            return {
                "success": True,
                "data": _format_repo(repo),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get repository {book_id}",
            }

    @mcp.tool()
    async def yuque_get_repo_by_path(group_login: str, book_slug: str) -> dict[str, Any]:
        """Get repository details using group login and book slug.

        This is useful when you know the repository's path but not its ID.
        The path format is: /groups/{group_login}/{book_slug}

        Args:
            group_login: The login name of the group (e.g., "my-team").
            book_slug: The slug identifier of the repository (e.g., "api-docs").

        Returns:
            Repository details including name, description, and metadata.

        Example:
            To get repository "api-docs" in group "engineering":
            {
                "group_login": "engineering",
                "book_slug": "api-docs"
            }
        """
        try:
            repo = client.repo.get_by_path(group_login=group_login, book_slug=book_slug)
            return {
                "success": True,
                "data": _format_repo(repo),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get repository {group_login}/{book_slug}",
            }

    @mcp.tool()
    async def yuque_list_repos(offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List all repositories accessible to the authenticated user.

        This returns repositories the user has created or has access to,
        including both personal and group repositories.

        Args:
            offset: Number of items to skip for pagination (default: 0).
            limit: Maximum number of items to return (default: 100, max: 100).

        Returns:
            List of repositories with pagination metadata.

        Example:
            To get the first 20 repositories:
            {
                "offset": 0,
                "limit": 20
            }
        """
        try:
            limit = min(limit, 100)
            result = client.repo.list(offset=offset, limit=limit)

            repos = [_format_repo(repo) for repo in result.data]

            return {
                "success": True,
                "data": {
                    "repositories": repos,
                    "total": result.meta.total if result.meta else len(repos),
                    "offset": offset,
                    "limit": limit,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list repositories",
            }

    @mcp.tool()
    async def yuque_get_user_repos(login: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """Get all repositories created by a specific user.

        This shows repositories owned by the specified user,
        both public and those accessible to the authenticated user.

        Args:
            login: The login name (username) of the user.
            offset: Number of items to skip for pagination (default: 0).
            limit: Maximum number of items to return (default: 100, max: 100).

        Returns:
            List of user's repositories with pagination metadata.

        Example:
            To get repositories created by user "john":
            {
                "login": "john",
                "offset": 0,
                "limit": 20
            }
        """
        try:
            limit = min(limit, 100)
            result = client.repo.get_user_repos(login=login, offset=offset, limit=limit)

            repos = [_format_repo(repo) for repo in result.data]

            return {
                "success": True,
                "data": {
                    "user": login,
                    "repositories": repos,
                    "total": result.meta.total if result.meta else len(repos),
                    "offset": offset,
                    "limit": limit,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get repositories for user {login}",
            }

    @mcp.tool()
    async def yuque_get_repo_toc(book_id: int) -> dict[str, Any]:
        """Get the table of contents (TOC) for a repository.

        The TOC shows the hierarchical structure of documents in the repository,
        including their titles, slugs, and nesting levels.

        Args:
            book_id: The unique identifier of the repository.

        Returns:
            Hierarchical table of contents with document references.

        Example:
            To get TOC for repository with ID 12345:
            {
                "book_id": 12345
            }
        """
        try:
            toc = client.repo.get_toc(book_id=book_id)
            toc_list: list[dict[str, Any]] = toc if isinstance(toc, list) else []

            return {
                "success": True,
                "data": {
                    "book_id": book_id,
                    "toc": [_format_toc_node(node) for node in toc_list],
                    "total_items": len(toc_list),
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get TOC for repository {book_id}",
            }

    @mcp.tool()
    async def yuque_get_repo_toc_by_path(group_login: str, book_slug: str) -> dict[str, Any]:
        """Get table of contents using group login and book slug.

        Useful when you know the repository path but not its ID.
        The path format is: /groups/{group_login}/{book_slug}

        Args:
            group_login: The login name of the group.
            book_slug: The slug identifier of the repository.

        Returns:
            Hierarchical table of contents with document references.

        Example:
            To get TOC for repository "api-docs" in group "engineering":
            {
                "group_login": "engineering",
                "book_slug": "api-docs"
            }
        """
        try:
            toc = client.repo.get_toc_by_path(group_login=group_login, book_slug=book_slug)
            toc_list: list[dict[str, Any]] = toc if isinstance(toc, list) else []

            return {
                "success": True,
                "data": {
                    "path": f"{group_login}/{book_slug}",
                    "toc": [_format_toc_node(node) for node in toc_list],
                    "total_items": len(toc_list),
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get TOC for repository {group_login}/{book_slug}",
            }


def _format_repo(repo: dict[str, Any]) -> dict[str, Any]:
    """Format repository data for better readability."""
    formatted: dict[str, Any] = {
        "id": repo.get("id"),
        "name": repo.get("name"),
        "slug": repo.get("slug"),
        "type": repo.get("type"),
        "description": repo.get("description"),
        "public": _get_public_label(repo.get("public", 0)),
        "creator_id": repo.get("creator_id"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
    }

    if repo.get("user"):
        formatted["creator"] = {
            "name": repo["user"].get("name"),
            "login": repo["user"].get("login"),
        }

    if repo.get("group"):
        formatted["group"] = {
            "name": repo["group"].get("name"),
            "login": repo["group"].get("login"),
        }

    return formatted


def _format_toc_node(node: dict[str, Any]) -> dict[str, Any]:
    """Format a TOC node with its children recursively."""
    formatted: dict[str, Any] = {
        "title": node.get("title"),
        "slug": node.get("slug"),
        "document_id": node.get("document_id"),
        "depth": node.get("depth", 1),
        "order": node.get("order", 0),
    }

    if node.get("children"):
        formatted["children"] = [_format_toc_node(child) for child in node["children"]]

    return formatted


def _get_public_label(public_level: int) -> str:
    """Convert public level to human-readable label."""
    labels = {
        0: "private",
        1: "public",
        2: "enterprise-wide",
    }
    return labels.get(public_level, f"unknown ({public_level})")
