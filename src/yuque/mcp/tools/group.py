"""Group-related MCP tools for Yuque API.

This module provides MCP tools for group operations in Yuque:
- Get group information
- Get group repositories
- Get group members
- Add group member
- Update group member role
- Remove group member
- Get group statistics
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

    from ...client import YuqueClient


def register_group_tools(mcp: FastMCP, client: YuqueClient) -> None:
    """Register all group-related MCP tools with the server.

    This function registers the following tools:
    - yuque_get_group: Get group information
    - yuque_get_group_repos: Get repositories in a group
    - yuque_get_group_members: Get group members
    - yuque_add_group_member: Add member to group
    - yuque_update_group_member: Update member role
    - yuque_remove_group_member: Remove member from group
    - yuque_get_group_statistics: Get group statistics

    Args:
        mcp: The FastMCP server instance to register tools with.
        client: Authenticated YuqueClient instance.

    Example:
        ```python
        from mcp.server.fastmcp import FastMCP
        from yuque import YuqueClient
        from yuque.mcp.tools.group import register_group_tools

        mcp = FastMCP("yuque-mcp")
        client = YuqueClient(token="your-token")
        register_group_tools(mcp, client)
        ```
    """

    @mcp.tool()
    async def yuque_get_group(login: str) -> str:
        """Get detailed information about a Yuque group/team.

        This tool retrieves comprehensive information about a specific group including
        its name, description, member count, and repository count.

        Args:
            login: The login name (slug) of the group. This is the unique identifier
                for the group in the URL (e.g., "my-team" in https://www.yuque.com/my-team).

        Returns:
            A formatted string containing group information including:
            - Group ID and login name
            - Display name and description
            - Owner information
            - Member count and repository count
            - Creation and update timestamps

        Example:
            >>> result = await yuque_get_group("my-team")
            >>> print(result)
            Group: My Team (my-team)
            ID: 12345
            Owner: John Doe (ID: 100)
            Members: 25 | Repositories: 10
        """
        try:
            group = client.group.get(login=login)

            lines = [
                f"Group: {group.get('name', 'N/A')} ({group.get('login', 'N/A')})",
                f"ID: {group.get('id', 'N/A')}",
                f"Owner ID: {group.get('owner_id', 'N/A')}",
                f"Members: {group.get('members_count', 0)} | Repositories: {group.get('books_count', 0)}",
            ]

            if description := group.get("description"):
                lines.append(f"Description: {description}")

            if created_at := group.get("created_at"):
                lines.append(f"Created: {created_at}")

            if updated_at := group.get("updated_at"):
                lines.append(f"Updated: {updated_at}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to get group '{login}': {e}"

    @mcp.tool()
    async def yuque_get_group_repos(
        login: str,
        offset: int = 0,
        limit: int = 100,
    ) -> str:
        """Get repositories (knowledge bases) in a Yuque group.

        This tool retrieves a paginated list of repositories belonging to a specific group.
        You can control pagination using offset and limit parameters.

        Args:
            login: The login name (slug) of the group.
            offset: The starting index for pagination (default: 0). Use this to skip
                    earlier results when navigating through pages.
            limit: Maximum number of repositories to return (default: 100, max: 100).
                  Set to a lower value for faster responses.

        Returns:
            A formatted string containing:
            - Total count of repositories
            - Repository list with name, slug, type, and visibility
            - Pagination information

        Example:
            >>> result = await yuque_get_group_repos("my-team", offset=0, limit=10)
            >>> print(result)
            Repositories in 'my-team': 10 total

            1. API Documentation (api-docs)
               Type: Book | Public: Yes | Docs: 25
        """
        try:
            result = client.group.get_repos(login=login, offset=offset, limit=limit)

            lines = [f"Repositories in '{login}': {len(result.data)} returned"]

            if result.meta:
                lines.append(
                    f"Total: {result.meta.total} | Page: {result.meta.page}/{result.meta.total_pages}"
                )

            lines.append("")

            for idx, repo in enumerate(result.data, 1):
                name = repo.get("name", "N/A")
                slug = repo.get("slug", "N/A")
                repo_type = repo.get("type", "Unknown")
                public = "Yes" if repo.get("public") == 1 else "No"
                doc_count = repo.get("doc_count", 0)

                lines.append(
                    f"{idx}. {name} ({slug})\n"
                    f"   Type: {repo_type} | Public: {public} | Docs: {doc_count}"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to get repositories for group '{login}': {e}"

    @mcp.tool()
    async def yuque_get_group_members(
        login: str,
        offset: int = 0,
        limit: int = 100,
    ) -> str:
        """Get members of a Yuque group.

        This tool retrieves a paginated list of members in a specific group,
        including their roles and user information.

        Member roles:
            - 0: Admin (full administrative access)
            - 1: Member (can edit and create content)
            - 2: Read-only (can only view content)

        Args:
            login: The login name (slug) of the group.
            offset: The starting index for pagination (default: 0).
            limit: Maximum number of members to return (default: 100).

        Returns:
            A formatted string containing:
            - Total member count
            - Member list with names, roles, and join dates
            - Pagination information

        Example:
            >>> result = await yuque_get_group_members("my-team")
            >>> print(result)
            Members of 'my-team': 25 total

            1. John Doe (ID: 100)
               Role: Admin | Joined: 2024-01-01
        """
        try:
            result = client.group.get_members(login=login, offset=offset, limit=limit)

            role_names = {0: "Admin", 1: "Member", 2: "Read-only"}

            lines = [f"Members of '{login}': {len(result.data)} returned"]

            if result.meta:
                lines.append(
                    f"Total: {result.meta.total} | Page: {result.meta.page}/{result.meta.total_pages}"
                )

            lines.append("")

            for idx, member in enumerate(result.data, 1):
                user = member.get("user", {})
                name = user.get("name", "N/A") if isinstance(user, dict) else "N/A"
                user_id = member.get("user_id", "N/A")
                role = member.get("role", 1)
                role_name = role_names.get(role, f"Unknown ({role})")
                created_at = member.get("created_at", "N/A")

                lines.append(
                    f"{idx}. {name} (ID: {user_id})\n   Role: {role_name} | Joined: {created_at}"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to get members for group '{login}': {e}"

    @mcp.tool()
    async def yuque_add_group_member(
        login: str,
        user_id: int,
        role: int = 1,
    ) -> str:
        """Add a new member to a Yuque group.

        This tool adds a user to a group with a specified role. You need admin
        privileges to add members to a group.

        Member roles:
            - 0: Admin (full administrative access, can manage members)
            - 1: Member (can edit and create content) - DEFAULT
            - 2: Read-only (can only view content)

        Args:
            login: The login name (slug) of the group.
            user_id: The ID of the user to add to the group.
            role: The role to assign to the new member (default: 1 for Member).
                  Use 0 for admin, 1 for member, 2 for read-only.

        Returns:
            A success message with the added member's information.

        Example:
            >>> result = await yuque_add_group_member("my-team", user_id=123, role=1)
            >>> print(result)
            ✅ Successfully added member to 'my-team'

            Member: John Doe (ID: 123)
            Role: Member
        """
        try:
            result = client.group.add_member(login=login, user_id=user_id, role=role)

            role_names = {0: "Admin", 1: "Member", 2: "Read-only"}
            role_name = role_names.get(role, f"Unknown ({role})")

            lines = [
                f"✅ Successfully added member to '{login}'",
                "",
            ]

            user = result.get("user", {})
            if isinstance(user, dict):
                user_name = user.get("name", "Unknown")
                lines.append(f"Member: {user_name} (ID: {user_id})")
            else:
                lines.append(f"Member ID: {user_id}")

            lines.append(f"Role: {role_name}")

            if created_at := result.get("created_at"):
                lines.append(f"Joined at: {created_at}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error: Failed to add member to group '{login}': {e}"

    @mcp.tool()
    async def yuque_update_group_member(
        login: str,
        user_id: int,
        role: int,
    ) -> str:
        """Update a group member's role.

        This tool changes the role of an existing group member. You need admin
        privileges to update member roles.

        Member roles:
            - 0: Admin (full administrative access, can manage members)
            - 1: Member (can edit and create content)
            - 2: Read-only (can only view content)

        Args:
            login: The login name (slug) of the group.
            user_id: The ID of the member to update.
            role: The new role to assign. Must be 0 (admin), 1 (member), or 2 (read-only).

        Returns:
            A success message with the updated member's information.

        Example:
            >>> result = await yuque_update_group_member("my-team", user_id=123, role=0)
            >>> print(result)
            ✅ Successfully updated member role in 'my-team'

            Member: John Doe (ID: 123)
            New Role: Admin
        """
        try:
            result = client.group.update_member(login=login, user_id=user_id, role=role)

            role_names = {0: "Admin", 1: "Member", 2: "Read-only"}
            role_name = role_names.get(role, f"Unknown ({role})")

            lines = [
                f"✅ Successfully updated member role in '{login}'",
                "",
            ]
            user = result.get("user", {})
            if isinstance(user, dict):
                user_name = user.get("name", "Unknown")
                lines.append(f"Member: {user_name} (ID: {user_id})")
            else:
                lines.append(f"Member ID: {user_id}")

            lines.append(f"New Role: {role_name}")

            if updated_at := result.get("updated_at"):
                lines.append(f"Updated at: {updated_at}")

            return "\n".join(lines)
        except Exception as e:
            return f"Error: Failed to update member in group '{login}': {e}"

    @mcp.tool()
    async def yuque_remove_group_member(
        login: str,
        user_id: int,
    ) -> str:
        """Remove a member from a Yuque group.

        This tool removes a user from a group. You need admin privileges to remove
        members. This action cannot be undone.

        **Warning**: This is a destructive operation. The member will lose access to
        all group resources immediately.

        Args:
            login: The login name (slug) of the group.
            user_id: The ID of the member to remove.

        Returns:
            A success message confirming the removal.

        Example:
            >>> result = await yuque_remove_group_member("my-team", user_id=123)
            >>> print(result)
            ✅ Successfully removed member from 'my-team'

            Removed User ID: 123
            Group: my-team

            ⚠️ Note: The user has lost access to all group resources.
        """
        try:
            client.group.remove_member(login=login, user_id=user_id)
            lines = [
                f"✅ Successfully removed member from '{login}'",
                "",
                f"Removed User ID: {user_id}",
                f"Group: {login}",
                "",
                "⚠️ Note: The user has lost access to all group resources.",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Error: Failed to remove member from group '{login}': {e}"

    @mcp.tool()
    async def yuque_get_group_statistics(login: str) -> str:
        """Get statistical information about a Yuque group.

        This tool retrieves comprehensive statistics about a group including
        document counts, member activity, and engagement metrics.

        Args:
            login: The login name (slug) of the group.

        Returns:
            A formatted string containing various statistics:
            - Total repositories and documents
            - Member count and activity
            - Views, likes, and comments

        Example:
            >>> result = await yuque_get_group_statistics("my-team")
            >>> print(result)
            Statistics for 'my-team'

            📊 Content:
            Repositories: 10
            Documents: 245

            👥 Members:
            Total Members: 25

            📈 Engagement:
            Total Views: 12,345
            Total Likes: 890
        """
        try:
            stats = client.group.get_statistics(login=login)
            lines = [
                f"Statistics for '{login}'",
                "",
                "📊 Content:",
                f"Repositories: {stats.get('books_count', 0)}",
                f"Documents: {stats.get('docs_count', 0)}",
            ]

            if public_docs := stats.get("public_docs_count"):
                lines.append(f"Public Documents: {public_docs}")

            lines.extend(
                [
                    "",
                    "👥 Members:",
                    f"Total Members: {stats.get('members_count', 0)}",
                ]
            )

            if admins := stats.get("admins_count"):
                lines.append(f"Admins: {admins}")
            if editors := stats.get("editors_count"):
                lines.append(f"Editors: {editors}")
            if readers := stats.get("readers_count"):
                lines.append(f"Readers: {readers}")

            lines.extend(
                [
                    "",
                    "📈 Engagement:",
                    f"Total Views: {stats.get('views_count', 0):,}",
                    f"Total Likes: {stats.get('likes_count', 0):,}",
                    f"Total Comments: {stats.get('comments_count', 0):,}",
                ]
            )

            if last_updated := stats.get("last_updated_at"):
                lines.extend(["", f"Last Updated: {last_updated}"])

            return "\n".join(lines)
        except Exception as e:
            return f"Error: Failed to get statistics for group '{login}': {e}"


__all__ = ["register_group_tools"]
