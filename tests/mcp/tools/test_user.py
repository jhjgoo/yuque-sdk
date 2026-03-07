"""Tests for User MCP tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from yuque.mcp.tools.user import (
    get_current_user,
    get_user,
    get_user_groups,
    register_user_tools,
)
from yuque.models import User


@pytest.fixture
def mock_client():
    """Create a mock YuqueClient."""
    client = MagicMock()
    client.user = MagicMock()
    client.user.get_me_async = AsyncMock()
    client.user.get_by_id_async = AsyncMock()
    client.user.get_groups = MagicMock()
    return client


@pytest.fixture
def sample_user():
    """Create a sample User instance."""
    from datetime import datetime

    return User(
        id=123456,
        login="testuser",
        name="Test User",
        email="test@example.com",
        avatar_url="https://example.com/avatar.png",
        html_url="https://www.yuque.com/testuser",
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        updated_at=datetime(2024, 1, 2, 15, 30, 0),
    )


@pytest.mark.asyncio
async def test_get_current_user_success(mock_client, sample_user):
    """Test getting current user successfully."""
    mock_client.user.get_me_async.return_value = sample_user

    result = await get_current_user(mock_client)

    assert "Current User Information" in result
    assert "123456" in result
    assert "testuser" in result
    assert "Test User" in result
    assert "test@example.com" in result
    mock_client.user.get_me_async.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_with_error(mock_client):
    """Test getting current user with error."""
    from yuque.exceptions import AuthenticationError

    mock_client.user.get_me_async.side_effect = AuthenticationError("Invalid token")

    result = await get_current_user(mock_client)

    assert "Error getting current user" in result
    assert "Invalid token" in result


@pytest.mark.asyncio
async def test_get_user_success(mock_client, sample_user):
    """Test getting user by ID successfully."""
    mock_client.user.get_by_id_async.return_value = sample_user

    result = await get_user(mock_client, user_id=123456)

    assert "User Information" in result
    assert "123456" in result
    assert "testuser" in result
    assert "Test User" in result
    mock_client.user.get_by_id_async.assert_called_once_with(123456)


@pytest.mark.asyncio
async def test_get_user_not_found(mock_client):
    """Test getting non-existent user."""
    from yuque.exceptions import NotFoundError

    mock_client.user.get_by_id_async.side_effect = NotFoundError("User not found")

    result = await get_user(mock_client, user_id=999999)

    assert "Error getting user 999999" in result
    assert "User not found" in result


@pytest.mark.asyncio
async def test_get_user_groups_success(mock_client):
    """Test getting user groups successfully."""
    groups = [
        {
            "id": 1,
            "login": "group1",
            "name": "Group One",
            "description": "First group",
            "members_count": 10,
            "books_count": 5,
            "avatar_url": "https://example.com/group1.png",
        },
        {
            "id": 2,
            "login": "group2",
            "name": "Group Two",
            "description": "Second group",
            "members_count": 20,
            "books_count": 8,
        },
    ]
    mock_client.user.get_groups.return_value = groups

    result = await get_user_groups(mock_client, user_id=123456)

    assert "User Groups" in result
    assert "Total groups: 2" in result
    assert "Group One" in result
    assert "Group Two" in result
    mock_client.user.get_groups.assert_called_once_with(123456, 0)


@pytest.mark.asyncio
async def test_get_user_groups_empty(mock_client):
    """Test getting user groups when user has no groups."""
    mock_client.user.get_groups.return_value = []

    result = await get_user_groups(mock_client, user_id=123456)

    assert "No groups found for user 123456" in result


@pytest.mark.asyncio
async def test_get_user_groups_with_error(mock_client):
    """Test getting user groups with error."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.user.get_groups.side_effect = PermissionDeniedError("Access denied")

    result = await get_user_groups(mock_client, user_id=123456)

    assert "Error getting groups for user 123456" in result
    assert "Access denied" in result


def test_register_user_tools():
    """Test that tools are registered correctly."""
    from mcp.server.fastmcp import FastMCP

    mock_client = MagicMock()
    mcp = FastMCP("test")

    register_user_tools(mcp, mock_client)

    assert len(mcp._tool_manager._tools) == 3
    tool_names = {tool.name for tool in mcp._tool_manager._tools.values()}
    assert "yuque_get_current_user" in tool_names
    assert "yuque_get_user" in tool_names
    assert "yuque_get_user_groups" in tool_names
