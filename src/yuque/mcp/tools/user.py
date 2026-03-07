"""User-related MCP tools for Yuque API.

This module provides MCP tools for user operations:
- Get current user information
- Get user by ID
- Get user's groups/teams
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..adapters import adapt_error

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ...client import YuqueClient


async def get_current_user(client: YuqueClient) -> str:
    """Get the current authenticated user's information.

    This tool retrieves detailed information about the currently authenticated user,
    including their ID, login name, display name, email, and profile URL.

    Args:
        client: Authenticated YuqueClient instance.

    Returns:
        Formatted user information including:
        - User ID and login name
        - Display name and email
        - Avatar URL and profile URL
        - Account creation and update timestamps

    Example:
        ```python
        user_info = await get_current_user(client)
        print(user_info)
        ```
    """
    try:
        user = await client.user.get_me_async()

        lines = [
            "# Current User Information",
            "",
            f"**User ID**: {user.id}",
            f"**Login**: {user.login}",
            f"**Name**: {user.name}",
        ]

        if user.email:
            lines.append(f"**Email**: {user.email}")

        if user.avatar_url:
            lines.append(f"**Avatar**: {user.avatar_url}")

        if user.html_url:
            lines.append(f"**Profile URL**: {user.html_url}")

        if user.created_at:
            lines.append(f"**Created At**: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if user.updated_at:
            lines.append(f"**Updated At**: {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    except Exception as e:
        error_response = adapt_error(e)
        return f"Error getting current user: {error_response['error']['message']}"


async def get_user(client: YuqueClient, user_id: int) -> str:
    """Get a specific user's information by their ID.

    This tool retrieves detailed information about a specific user using their
    unique identifier. Useful for looking up user profiles or verifying user
    information.

    Args:
        client: Authenticated YuqueClient instance.
        user_id: The unique identifier of the user to retrieve.

    Returns:
        Formatted user information including:
        - User ID and login name
        - Display name and email
        - Avatar URL and profile URL
        - Account creation and update timestamps

    Raises:
        NotFoundError: If the user with the specified ID does not exist.
        PermissionDeniedError: If you don't have permission to view this user.

    Example:
        ```python
        user_info = await get_user(client, user_id=123456)
        print(user_info)
        ```
    """
    try:
        user = await client.user.get_by_id_async(user_id)

        lines = [
            f"# User Information (ID: {user_id})",
            "",
            f"**User ID**: {user.id}",
            f"**Login**: {user.login}",
            f"**Name**: {user.name}",
        ]

        if user.email:
            lines.append(f"**Email**: {user.email}")

        if user.avatar_url:
            lines.append(f"**Avatar**: {user.avatar_url}")

        if user.html_url:
            lines.append(f"**Profile URL**: {user.html_url}")

        if user.created_at:
            lines.append(f"**Created At**: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if user.updated_at:
            lines.append(f"**Updated At**: {user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    except Exception as e:
        error_response = adapt_error(e)
        return f"Error getting user {user_id}: {error_response['error']['message']}"


async def get_user_groups(client: YuqueClient, user_id: int, offset: int = 0) -> str:
    """Get the list of groups/teams that a user belongs to.

    This tool retrieves all the groups and teams that a specific user is a member of.
    Groups represent organizations or teams in Yuque where users can collaborate
    on documents and knowledge bases.

    Args:
        client: Authenticated YuqueClient instance.
        user_id: The unique identifier of the user.
        offset: Pagination offset for large result sets (default: 0).

    Returns:
        Formatted list of groups including:
        - Group ID and login/slug
        - Group name and description
        - Member count and book count
        - Avatar URL

    Example:
        ```python
        groups = await get_user_groups(client, user_id=123456)
        print(groups)
        ```
    """
    try:
        import asyncio

        groups = await asyncio.get_event_loop().run_in_executor(
            None, lambda: client.user.get_groups(user_id, offset)
        )

        if not groups:
            return f"No groups found for user {user_id}."

        lines = [
            f"# User Groups (User ID: {user_id})",
            "",
            f"Total groups: {len(groups)}",
            "",
        ]

        for idx, group in enumerate(groups, 1):
            group_id = group.get("id", "N/A")
            login = group.get("login", "N/A")
            name = group.get("name", "N/A")
            description = group.get("description", "")
            members_count = group.get("members_count", 0)
            books_count = group.get("books_count", 0)
            avatar_url = group.get("avatar_url", "")

            lines.append(f"## {idx}. {name}")
            lines.append(f"- **Group ID**: {group_id}")
            lines.append(f"- **Login**: {login}")

            if description:
                lines.append(f"- **Description**: {description}")

            lines.append(f"- **Members**: {members_count}")
            lines.append(f"- **Knowledge Bases**: {books_count}")

            if avatar_url:
                lines.append(f"- **Avatar**: {avatar_url}")

            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        error_response = adapt_error(e)
        return f"Error getting groups for user {user_id}: {error_response['error']['message']}"


def register_user_tools(mcp: FastMCP, client: YuqueClient) -> None:
    """Register all user-related MCP tools with the server.

    This function registers the following tools:
    - yuque_get_current_user: Get current authenticated user
    - yuque_get_user: Get user by ID
    - yuque_get_user_groups: Get user's groups/teams

    Args:
        mcp: The FastMCP server instance to register tools with.
        client: Authenticated YuqueClient instance.

    Example:
        ```python
        from mcp.server.fastmcp import FastMCP
        from yuque import YuqueClient
        from yuque.mcp.tools.user import register_user_tools

        mcp = FastMCP("yuque-mcp")
        client = YuqueClient(token="your-token")
        register_user_tools(mcp, client)
        ```
    """

    @mcp.tool()
    async def yuque_get_current_user() -> str:
        """Get the current authenticated user's information.

        Retrieves detailed information about the currently authenticated user,
        including ID, login, name, email, and profile details.

        Returns:
            Formatted user information as markdown text.
        """
        return await get_current_user(client)

    @mcp.tool()
    async def yuque_get_user(user_id: int) -> str:
        """Get a specific user's information by their ID.

        Retrieves detailed information about a specific user using their
        unique identifier.

        Args:
            user_id: The unique identifier of the user to retrieve.

        Returns:
            Formatted user information as markdown text.
        """
        return await get_user(client, user_id)

    @mcp.tool()
    async def yuque_get_user_groups(user_id: int, offset: int = 0) -> str:
        """Get the list of groups/teams that a user belongs to.

        Retrieves all the groups and teams that a specific user is a member of.
        Groups represent organizations or teams in Yuque for collaboration.

        Args:
            user_id: The unique identifier of the user.
            offset: Pagination offset for large result sets (default: 0).

        Returns:
            Formatted list of groups as markdown text.
        """
        return await get_user_groups(client, user_id, offset)
