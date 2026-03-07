"""Tests for Group MCP tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from yuque.mcp.tools.group import register_group_tools
from yuque.models import PaginationMeta, PaginatedResponse


@pytest.fixture
def mock_client():
    """Create a mock YuqueClient."""
    client = MagicMock()
    client.group = MagicMock()
    client.group.get = MagicMock()
    client.group.get_repos = MagicMock()
    client.group.get_members = MagicMock()
    client.group.add_member = MagicMock()
    client.group.update_member = MagicMock()
    client.group.remove_member = MagicMock()
    client.group.get_statistics = MagicMock()
    return client


@pytest.fixture
def mock_mcp():
    """Create a mock FastMCP instance."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


@pytest.fixture
def sample_group():
    """Create a sample group response."""
    return {
        "id": 12345,
        "login": "test-team",
        "name": "Test Team",
        "description": "A test team for unit testing",
        "owner_id": 100,
        "members_count": 25,
        "books_count": 10,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-06-15T14:30:00Z",
    }


@pytest.fixture
def sample_repos():
    """Create sample repository data."""
    return [
        {
            "id": 1,
            "name": "API Documentation",
            "slug": "api-docs",
            "type": "Book",
            "public": 1,
            "doc_count": 45,
        },
        {
            "id": 2,
            "name": "Internal Wiki",
            "slug": "internal-wiki",
            "type": "Book",
            "public": 0,
            "doc_count": 120,
        },
    ]


@pytest.fixture
def sample_members():
    """Create sample member data."""
    return [
        {
            "user_id": 101,
            "user": {"id": 101, "name": "Admin User", "login": "admin"},
            "role": 0,
            "created_at": "2024-01-15T08:00:00Z",
        },
        {
            "user_id": 102,
            "user": {"id": 102, "name": "Regular Member", "login": "member"},
            "role": 1,
            "created_at": "2024-02-20T09:30:00Z",
        },
        {
            "user_id": 103,
            "user": {"id": 103, "name": "Read Only User", "login": "reader"},
            "role": 2,
            "created_at": "2024-03-10T11:00:00Z",
        },
    ]


@pytest.fixture
def sample_statistics():
    """Create sample group statistics."""
    return {
        "books_count": 10,
        "docs_count": 245,
        "public_docs_count": 50,
        "members_count": 25,
        "admins_count": 3,
        "editors_count": 10,
        "readers_count": 12,
        "views_count": 12345,
        "likes_count": 890,
        "comments_count": 156,
        "last_updated_at": "2024-06-20T16:00:00Z",
    }


def create_paginated_response(data, total=None, page=1, per_page=20):
    """Helper to create a PaginatedResponse."""
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total or len(data),
        total_pages=(total or len(data) + per_page - 1) // per_page if per_page > 0 else 0,
    )
    return PaginatedResponse(data=data, meta=meta)


# ============================================================
# Tests for yuque_get_group
# ============================================================


@pytest.mark.asyncio
async def test_get_group_success(mock_client, sample_group):
    """Test getting group information successfully."""
    mock_client.group.get.return_value = sample_group

    # Register tools and get the tool function
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    # Get the tool function
    tools = list(mcp._tool_manager._tools.values())
    get_group_tool = next(t for t in tools if t.name == "yuque_get_group")

    result = await get_group_tool.fn(login="test-team")

    assert "Test Team" in result
    assert "test-team" in result
    assert "12345" in result
    assert "25" in result
    assert "10" in result
    assert "A test team for unit testing" in result
    mock_client.group.get.assert_called_once_with(login="test-team")


@pytest.mark.asyncio
async def test_get_group_minimal_info(mock_client):
    """Test getting group with minimal information."""
    mock_client.group.get.return_value = {
        "id": 999,
        "login": "minimal-team",
        "name": "Minimal",
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_group_tool = next(t for t in tools if t.name == "yuque_get_group")

    result = await get_group_tool.fn(login="minimal-team")

    assert "Minimal" in result
    assert "minimal-team" in result
    assert "999" in result


@pytest.mark.asyncio
async def test_get_group_not_found(mock_client):
    """Test getting non-existent group."""
    from yuque.exceptions import NotFoundError

    mock_client.group.get.side_effect = NotFoundError("Group not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_group_tool = next(t for t in tools if t.name == "yuque_get_group")

    result = await get_group_tool.fn(login="nonexistent")

    assert result.startswith("Error:")
    assert "nonexistent" in result
    assert "Group not found" in result


@pytest.mark.asyncio
async def test_get_group_permission_denied(mock_client):
    """Test getting group without permission."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.group.get.side_effect = PermissionDeniedError("Access denied")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_group_tool = next(t for t in tools if t.name == "yuque_get_group")

    result = await get_group_tool.fn(login="private-team")

    assert result.startswith("Error:")
    assert "Access denied" in result


# ============================================================
# Tests for yuque_get_group_repos
# ============================================================


@pytest.mark.asyncio
async def test_get_group_repos_success(mock_client, sample_repos):
    """Test getting group repositories successfully."""
    mock_client.group.get_repos.return_value = create_paginated_response(sample_repos, total=2)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_repos_tool = next(t for t in tools if t.name == "yuque_get_group_repos")

    result = await get_repos_tool.fn(login="test-team")

    assert "Repositories in 'test-team'" in result
    assert "2 returned" in result
    assert "API Documentation" in result
    assert "api-docs" in result
    assert "Internal Wiki" in result
    mock_client.group.get_repos.assert_called_once_with(login="test-team", offset=0, limit=100)


@pytest.mark.asyncio
async def test_get_group_repos_with_pagination(mock_client, sample_repos):
    """Test getting group repositories with custom pagination."""
    mock_client.group.get_repos.return_value = create_paginated_response(
        sample_repos, total=50, page=2
    )

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_repos_tool = next(t for t in tools if t.name == "yuque_get_group_repos")

    result = await get_repos_tool.fn(login="test-team", offset=10, limit=10)

    assert "Total: 50" in result
    assert "Page: 2" in result
    mock_client.group.get_repos.assert_called_once_with(login="test-team", offset=10, limit=10)


@pytest.mark.asyncio
async def test_get_group_repos_empty(mock_client):
    """Test getting group repositories when empty."""
    mock_client.group.get_repos.return_value = create_paginated_response([])

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_repos_tool = next(t for t in tools if t.name == "yuque_get_group_repos")

    result = await get_repos_tool.fn(login="empty-team")

    assert "0 returned" in result


@pytest.mark.asyncio
async def test_get_group_repos_with_error(mock_client):
    """Test getting group repositories with error."""
    from yuque.exceptions import NotFoundError

    mock_client.group.get_repos.side_effect = NotFoundError("Group not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_repos_tool = next(t for t in tools if t.name == "yuque_get_group_repos")

    result = await get_repos_tool.fn(login="nonexistent")

    assert result.startswith("Error:")
    assert "nonexistent" in result


@pytest.mark.asyncio
async def test_get_group_repos_visibility_flags(mock_client):
    """Test repository visibility flags."""
    repos = [
        {
            "id": 1,
            "name": "Public Repo",
            "slug": "public",
            "type": "Book",
            "public": 1,
            "doc_count": 10,
        },
        {
            "id": 2,
            "name": "Private Repo",
            "slug": "private",
            "type": "Book",
            "public": 0,
            "doc_count": 5,
        },
    ]
    mock_client.group.get_repos.return_value = create_paginated_response(repos)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_repos_tool = next(t for t in tools if t.name == "yuque_get_group_repos")

    result = await get_repos_tool.fn(login="test-team")

    assert "Public: Yes" in result
    assert "Public: No" in result


# ============================================================
# Tests for yuque_get_group_members
# ============================================================


@pytest.mark.asyncio
async def test_get_group_members_success(mock_client, sample_members):
    """Test getting group members successfully."""
    mock_client.group.get_members.return_value = create_paginated_response(sample_members, total=3)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="test-team")

    assert "Members of 'test-team'" in result
    assert "3 returned" in result
    assert "Admin User" in result
    assert "Regular Member" in result
    assert "Read Only User" in result
    mock_client.group.get_members.assert_called_once_with(login="test-team", offset=0, limit=100)


@pytest.mark.asyncio
async def test_get_group_members_role_labels(mock_client):
    """Test that role labels are correctly mapped."""
    members = [
        {"user_id": 1, "user": {"name": "Admin"}, "role": 0, "created_at": "2024-01-01"},
        {"user_id": 2, "user": {"name": "Member"}, "role": 1, "created_at": "2024-01-01"},
        {"user_id": 3, "user": {"name": "Reader"}, "role": 2, "created_at": "2024-01-01"},
    ]
    mock_client.group.get_members.return_value = create_paginated_response(members)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="test-team")

    assert "Role: Admin" in result
    assert "Role: Member" in result
    assert "Role: Read-only" in result


@pytest.mark.asyncio
async def test_get_group_members_empty(mock_client):
    """Test getting members when group has no members."""
    mock_client.group.get_members.return_value = create_paginated_response([])

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="empty-team")

    assert "0 returned" in result


@pytest.mark.asyncio
async def test_get_group_members_with_pagination(mock_client, sample_members):
    """Test getting members with pagination."""
    mock_client.group.get_members.return_value = create_paginated_response(
        sample_members, total=100, page=1
    )

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="test-team", offset=20, limit=20)

    assert "Total: 100" in result
    mock_client.group.get_members.assert_called_once_with(login="test-team", offset=20, limit=20)


@pytest.mark.asyncio
async def test_get_group_members_with_error(mock_client):
    """Test getting members with error."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.group.get_members.side_effect = PermissionDeniedError("Access denied")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="private-team")

    assert result.startswith("Error:")
    assert "private-team" in result


@pytest.mark.asyncio
async def test_get_group_members_unknown_role(mock_client):
    """Test handling of unknown role values."""
    members = [
        {"user_id": 1, "user": {"name": "Unknown"}, "role": 99, "created_at": "2024-01-01"},
    ]
    mock_client.group.get_members.return_value = create_paginated_response(members)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="test-team")

    assert "Unknown (99)" in result


@pytest.mark.asyncio
async def test_get_group_members_missing_user_info(mock_client):
    """Test handling members with missing user info."""
    members = [
        {"user_id": 1, "user": None, "role": 1, "created_at": "2024-01-01"},
        {"user_id": 2, "user": "invalid", "role": 1, "created_at": "2024-01-01"},
    ]
    mock_client.group.get_members.return_value = create_paginated_response(members)

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_members_tool = next(t for t in tools if t.name == "yuque_get_group_members")

    result = await get_members_tool.fn(login="test-team")

    assert "N/A" in result


# ============================================================
# Tests for yuque_add_group_member
# ============================================================


@pytest.mark.asyncio
async def test_add_group_member_success(mock_client):
    """Test adding member to group successfully."""
    mock_client.group.add_member.return_value = {
        "user": {"id": 123, "name": "New Member"},
        "role": 1,
        "created_at": "2024-06-20T10:00:00Z",
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    add_member_tool = next(t for t in tools if t.name == "yuque_add_group_member")

    result = await add_member_tool.fn(login="test-team", user_id=123, role=1)

    assert "✅" in result
    assert "Successfully added member" in result
    assert "test-team" in result
    assert "New Member" in result
    assert "123" in result
    assert "Role: Member" in result
    mock_client.group.add_member.assert_called_once_with(login="test-team", user_id=123, role=1)


@pytest.mark.asyncio
async def test_add_group_member_as_admin(mock_client):
    """Test adding member with admin role."""
    mock_client.group.add_member.return_value = {
        "user": {"id": 456, "name": "New Admin"},
        "role": 0,
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    add_member_tool = next(t for t in tools if t.name == "yuque_add_group_member")

    result = await add_member_tool.fn(login="test-team", user_id=456, role=0)

    assert "✅" in result
    assert "Role: Admin" in result


@pytest.mark.asyncio
async def test_add_group_member_as_readonly(mock_client):
    """Test adding member with read-only role."""
    mock_client.group.add_member.return_value = {
        "user": {"id": 789, "name": "Reader"},
        "role": 2,
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    add_member_tool = next(t for t in tools if t.name == "yuque_add_group_member")

    result = await add_member_tool.fn(login="test-team", user_id=789, role=2)

    assert "✅" in result
    assert "Role: Read-only" in result


@pytest.mark.asyncio
async def test_add_group_member_with_error(mock_client):
    """Test adding member with error."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.group.add_member.side_effect = PermissionDeniedError("You don't have permission")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    add_member_tool = next(t for t in tools if t.name == "yuque_add_group_member")

    result = await add_member_tool.fn(login="test-team", user_id=123, role=1)

    assert result.startswith("Error:")
    assert "test-team" in result


@pytest.mark.asyncio
async def test_add_group_member_missing_user_info(mock_client):
    """Test adding member when user info is missing."""
    mock_client.group.add_member.return_value = {
        "user": None,
        "role": 1,
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    add_member_tool = next(t for t in tools if t.name == "yuque_add_group_member")

    result = await add_member_tool.fn(login="test-team", user_id=999, role=1)

    assert "Member ID: 999" in result


# ============================================================
# Tests for yuque_update_group_member
# ============================================================


@pytest.mark.asyncio
async def test_update_group_member_success(mock_client):
    """Test updating member role successfully."""
    mock_client.group.update_member.return_value = {
        "user": {"id": 123, "name": "Updated User"},
        "role": 0,
        "updated_at": "2024-06-20T12:00:00Z",
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    update_member_tool = next(t for t in tools if t.name == "yuque_update_group_member")

    result = await update_member_tool.fn(login="test-team", user_id=123, role=0)

    assert "✅" in result
    assert "Successfully updated member role" in result
    assert "test-team" in result
    assert "Updated User" in result
    assert "New Role: Admin" in result
    mock_client.group.update_member.assert_called_once_with(login="test-team", user_id=123, role=0)


@pytest.mark.asyncio
async def test_update_group_member_to_readonly(mock_client):
    """Test updating member to read-only role."""
    mock_client.group.update_member.return_value = {
        "user": {"id": 456, "name": "Downgraded User"},
        "role": 2,
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    update_member_tool = next(t for t in tools if t.name == "yuque_update_group_member")

    result = await update_member_tool.fn(login="test-team", user_id=456, role=2)

    assert "✅" in result
    assert "New Role: Read-only" in result


@pytest.mark.asyncio
async def test_update_group_member_with_error(mock_client):
    """Test updating member with error."""
    from yuque.exceptions import NotFoundError

    mock_client.group.update_member.side_effect = NotFoundError("Member not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    update_member_tool = next(t for t in tools if t.name == "yuque_update_group_member")

    result = await update_member_tool.fn(login="test-team", user_id=999, role=1)

    assert result.startswith("Error:")
    assert "test-team" in result


# ============================================================
# Tests for yuque_remove_group_member
# ============================================================


@pytest.mark.asyncio
async def test_remove_group_member_success(mock_client):
    """Test removing member from group successfully."""
    mock_client.group.remove_member.return_value = None

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    remove_member_tool = next(t for t in tools if t.name == "yuque_remove_group_member")

    result = await remove_member_tool.fn(login="test-team", user_id=123)

    assert "✅" in result
    assert "Successfully removed member" in result
    assert "test-team" in result
    assert "Removed User ID: 123" in result
    assert "⚠️" in result
    assert "lost access" in result
    mock_client.group.remove_member.assert_called_once_with(login="test-team", user_id=123)


@pytest.mark.asyncio
async def test_remove_group_member_with_error(mock_client):
    """Test removing member with error."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.group.remove_member.side_effect = PermissionDeniedError("Cannot remove last admin")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    remove_member_tool = next(t for t in tools if t.name == "yuque_remove_group_member")

    result = await remove_member_tool.fn(login="test-team", user_id=1)

    assert result.startswith("Error:")
    assert "test-team" in result


@pytest.mark.asyncio
async def test_remove_group_member_warning_message(mock_client):
    """Test that warning message is included in remove response."""
    mock_client.group.remove_member.return_value = None

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    remove_member_tool = next(t for t in tools if t.name == "yuque_remove_group_member")

    result = await remove_member_tool.fn(login="test-team", user_id=456)

    assert "⚠️ Note:" in result
    assert "lost access to all group resources" in result


# ============================================================
# Tests for yuque_get_group_statistics
# ============================================================


@pytest.mark.asyncio
async def test_get_group_statistics_success(mock_client, sample_statistics):
    """Test getting group statistics successfully."""
    mock_client.group.get_statistics.return_value = sample_statistics

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Statistics for 'test-team'" in result
    assert "📊 Content:" in result
    assert "👥 Members:" in result
    assert "📈 Engagement:" in result
    mock_client.group.get_statistics.assert_called_once_with(login="test-team")


@pytest.mark.asyncio
async def test_get_group_statistics_content_section(mock_client, sample_statistics):
    """Test statistics content section formatting."""
    mock_client.group.get_statistics.return_value = sample_statistics

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Repositories: 10" in result
    assert "Documents: 245" in result
    assert "Public Documents: 50" in result


@pytest.mark.asyncio
async def test_get_group_statistics_members_section(mock_client, sample_statistics):
    """Test statistics members section formatting."""
    mock_client.group.get_statistics.return_value = sample_statistics

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Total Members: 25" in result
    assert "Admins: 3" in result
    assert "Editors: 10" in result
    assert "Readers: 12" in result


@pytest.mark.asyncio
async def test_get_group_statistics_engagement_section(mock_client, sample_statistics):
    """Test statistics engagement section formatting."""
    mock_client.group.get_statistics.return_value = sample_statistics

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Total Views: 12,345" in result  # Check number formatting
    assert "Total Likes: 890" in result
    assert "Total Comments: 156" in result


@pytest.mark.asyncio
async def test_get_group_statistics_with_last_updated(mock_client, sample_statistics):
    """Test statistics with last updated timestamp."""
    mock_client.group.get_statistics.return_value = sample_statistics

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Last Updated: 2024-06-20T16:00:00Z" in result


@pytest.mark.asyncio
async def test_get_group_statistics_minimal(mock_client):
    """Test statistics with minimal data."""
    mock_client.group.get_statistics.return_value = {
        "books_count": 5,
        "docs_count": 100,
        "members_count": 10,
        "views_count": 1000,
        "likes_count": 50,
        "comments_count": 20,
    }

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="test-team")

    assert "Repositories: 5" in result
    assert "Documents: 100" in result
    assert "Total Members: 10" in result
    assert "Total Views: 1,000" in result


@pytest.mark.asyncio
async def test_get_group_statistics_with_error(mock_client):
    """Test getting statistics with error."""
    from yuque.exceptions import NotFoundError

    mock_client.group.get_statistics.side_effect = NotFoundError("Group not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_group_tools(mcp, mock_client)

    tools = list(mcp._tool_manager._tools.values())
    get_stats_tool = next(t for t in tools if t.name == "yuque_get_group_statistics")

    result = await get_stats_tool.fn(login="nonexistent")

    assert result.startswith("Error:")
    assert "nonexistent" in result


# ============================================================
# Tests for tool registration
# ============================================================


def test_register_group_tools(mock_mcp, mock_client):
    """Test that all group tools are registered correctly."""
    register_group_tools(mock_mcp, mock_client)

    tool_names = {tool.name for tool in mock_mcp._tool_manager._tools.values()}

    assert len(mock_mcp._tool_manager._tools) == 7
    assert "yuque_get_group" in tool_names
    assert "yuque_get_group_repos" in tool_names
    assert "yuque_get_group_members" in tool_names
    assert "yuque_add_group_member" in tool_names
    assert "yuque_update_group_member" in tool_names
    assert "yuque_remove_group_member" in tool_names
    assert "yuque_get_group_statistics" in tool_names


def test_tool_descriptions(mock_mcp, mock_client):
    """Test that tools have proper descriptions."""
    register_group_tools(mock_mcp, mock_client)

    for tool in mock_mcp._tool_manager._tools.values():
        assert tool.description is not None
        assert len(tool.description) > 20  # Should have meaningful descriptions
