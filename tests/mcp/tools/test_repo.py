"""Tests for Repository MCP tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yuque.mcp.tools.repo import (
    _format_repo,
    _format_toc_node,
    _get_public_label,
    register_repo_tools,
)


@pytest.fixture
def mock_client():
    """Create a mock YuqueClient."""
    client = MagicMock()
    client.repo = MagicMock()
    client.repo.get = MagicMock()
    client.repo.get_by_path = MagicMock()
    client.repo.list = MagicMock()
    client.repo.get_user_repos = MagicMock()
    client.repo.get_group_repos = MagicMock()
    client.repo.get_toc = MagicMock()
    client.repo.get_toc_by_path = MagicMock()
    return client


@pytest.fixture
def sample_repo():
    """Create a sample repository dict."""
    return {
        "id": 12345,
        "name": "Test Repository",
        "slug": "test-repo",
        "type": "Book",
        "description": "A test repository",
        "public": 1,
        "creator_id": 789,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-02T15:30:00Z",
        "user": {
            "name": "Test User",
            "login": "testuser",
        },
        "group": {
            "name": "Test Group",
            "login": "testgroup",
        },
    }


@pytest.fixture
def sample_repo_minimal():
    """Create a minimal repository dict."""
    return {
        "id": 54321,
        "name": "Minimal Repo",
        "slug": "minimal-repo",
        "type": "Book",
        "public": 0,
    }


@pytest.fixture
def sample_toc():
    """Create a sample TOC with nested structure."""
    return [
        {
            "title": "Introduction",
            "slug": "intro",
            "document_id": 100,
            "depth": 1,
            "order": 0,
        },
        {
            "title": "Chapter 1",
            "slug": "chapter-1",
            "document_id": 101,
            "depth": 1,
            "order": 1,
            "children": [
                {
                    "title": "Section 1.1",
                    "slug": "section-1-1",
                    "document_id": 102,
                    "depth": 2,
                    "order": 0,
                    "children": [
                        {
                            "title": "Subsection 1.1.1",
                            "slug": "subsection-1-1-1",
                            "document_id": 103,
                            "depth": 3,
                            "order": 0,
                        }
                    ],
                }
            ],
        },
    ]


@pytest.fixture
def mock_mcp():
    """Create a mock FastMCP instance."""
    from mcp.server.fastmcp import FastMCP

    return FastMCP("test")


# ============================================
# Helper Function Tests
# ============================================


def test_format_repo_complete(sample_repo):
    """Test _format_repo with complete repository data."""
    result = _format_repo(sample_repo)

    assert result["id"] == 12345
    assert result["name"] == "Test Repository"
    assert result["slug"] == "test-repo"
    assert result["type"] == "Book"
    assert result["description"] == "A test repository"
    assert result["public"] == "public"
    assert result["creator_id"] == 789
    assert result["creator"]["name"] == "Test User"
    assert result["creator"]["login"] == "testuser"
    assert result["group"]["name"] == "Test Group"
    assert result["group"]["login"] == "testgroup"


def test_format_repo_minimal(sample_repo_minimal):
    """Test _format_repo with minimal repository data."""
    result = _format_repo(sample_repo_minimal)

    assert result["id"] == 54321
    assert result["name"] == "Minimal Repo"
    assert result["slug"] == "minimal-repo"
    assert result["public"] == "private"
    assert "creator" not in result
    assert "group" not in result


def test_format_repo_without_user_or_group():
    """Test _format_repo without user or group data."""
    repo = {
        "id": 999,
        "name": "Solo Repo",
        "slug": "solo",
        "public": 2,
    }
    result = _format_repo(repo)

    assert result["id"] == 999
    assert result["public"] == "enterprise-wide"
    assert "creator" not in result
    assert "group" not in result


def test_format_toc_node_simple():
    """Test _format_toc_node with simple node."""
    node = {
        "title": "Simple Node",
        "slug": "simple",
        "document_id": 123,
        "depth": 1,
        "order": 0,
    }
    result = _format_toc_node(node)

    assert result["title"] == "Simple Node"
    assert result["slug"] == "simple"
    assert result["document_id"] == 123
    assert result["depth"] == 1
    assert result["order"] == 0
    assert "children" not in result


def test_format_toc_node_with_children(sample_toc):
    """Test _format_toc_node with nested children."""
    result = _format_toc_node(sample_toc[1])  # Chapter 1 with children

    assert result["title"] == "Chapter 1"
    assert result["slug"] == "chapter-1"
    assert "children" in result
    assert len(result["children"]) == 1
    assert result["children"][0]["title"] == "Section 1.1"


def test_format_toc_node_deeply_nested(sample_toc):
    """Test _format_toc_node with deeply nested children."""
    result = _format_toc_node(sample_toc[1])  # Chapter 1

    # Navigate to deepest level
    section = result["children"][0]
    subsection = section["children"][0]

    assert subsection["title"] == "Subsection 1.1.1"
    assert subsection["depth"] == 3
    assert "children" not in subsection


def test_format_toc_node_missing_fields():
    """Test _format_toc_node with missing optional fields."""
    node = {"title": "Incomplete Node", "slug": "incomplete"}
    result = _format_toc_node(node)

    assert result["title"] == "Incomplete Node"
    assert result["depth"] == 1  # Default value
    assert result["order"] == 0  # Default value


def test_get_public_label():
    """Test _get_public_label for all public levels."""
    assert _get_public_label(0) == "private"
    assert _get_public_label(1) == "public"
    assert _get_public_label(2) == "enterprise-wide"


def test_get_public_label_unknown():
    """Test _get_public_label with unknown level."""
    assert _get_public_label(99) == "unknown (99)"
    assert _get_public_label(-1) == "unknown (-1)"


# ============================================
# Tool: yuque_get_repo
# ============================================


@pytest.mark.asyncio
async def test_yuque_get_repo_success(mock_mcp, mock_client, sample_repo):
    """Test getting repository by ID successfully."""
    mock_client.repo.get.return_value = sample_repo

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_repo_tool = next(t for t in tools if t.name == "yuque_get_repo")

    result = await get_repo_tool.fn(book_id=12345)

    assert result["success"] is True
    assert result["data"]["id"] == 12345
    assert result["data"]["name"] == "Test Repository"
    mock_client.repo.get.assert_called_once_with(book_id=12345)


@pytest.mark.asyncio
async def test_yuque_get_repo_not_found(mock_mcp, mock_client):
    """Test getting non-existent repository."""
    from yuque.exceptions import NotFoundError

    mock_client.repo.get.side_effect = NotFoundError("Repository not found")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_repo_tool = next(t for t in tools if t.name == "yuque_get_repo")

    result = await get_repo_tool.fn(book_id=999999)

    assert result["success"] is False
    assert "Repository not found" in result["error"]
    assert "Failed to get repository 999999" in result["message"]


@pytest.mark.asyncio
async def test_yuque_get_repo_permission_denied(mock_mcp, mock_client):
    """Test getting repository without permission."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.repo.get.side_effect = PermissionDeniedError("Access denied")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_repo_tool = next(t for t in tools if t.name == "yuque_get_repo")

    result = await get_repo_tool.fn(book_id=12345)

    assert result["success"] is False
    assert "Access denied" in result["error"]


# ============================================
# Tool: yuque_get_repo_by_path
# ============================================


@pytest.mark.asyncio
async def test_yuque_get_repo_by_path_success(mock_mcp, mock_client, sample_repo):
    """Test getting repository by path successfully."""
    mock_client.repo.get_by_path.return_value = sample_repo

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_repo_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_by_path")

    result = await get_repo_by_path_tool.fn(group_login="testgroup", book_slug="test-repo")

    assert result["success"] is True
    assert result["data"]["id"] == 12345
    mock_client.repo.get_by_path.assert_called_once_with(
        group_login="testgroup", book_slug="test-repo"
    )


@pytest.mark.asyncio
async def test_yuque_get_repo_by_path_not_found(mock_mcp, mock_client):
    """Test getting repository by non-existent path."""
    from yuque.exceptions import NotFoundError

    mock_client.repo.get_by_path.side_effect = NotFoundError("Repository not found")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_repo_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_by_path")

    result = await get_repo_by_path_tool.fn(group_login="unknown", book_slug="missing")

    assert result["success"] is False
    assert "Repository not found" in result["error"]
    assert "Failed to get repository unknown/missing" in result["message"]


# ============================================
# Tool: yuque_list_repos
# ============================================


@pytest.mark.asyncio
async def test_yuque_list_repos_success(mock_mcp, mock_client, sample_repo):
    """Test listing repositories successfully."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = [sample_repo]
    mock_result.meta = PaginationMeta(total=1)
    mock_client.repo.list.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn(offset=0, limit=20)

    assert result["success"] is True
    assert len(result["data"]["repositories"]) == 1
    assert result["data"]["total"] == 1
    assert result["data"]["offset"] == 0
    assert result["data"]["limit"] == 20
    mock_client.repo.list.assert_called_once_with(offset=0, limit=20)


@pytest.mark.asyncio
async def test_yuque_list_repos_with_pagination(mock_mcp, mock_client, sample_repo):
    """Test listing repositories with pagination."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = [sample_repo]
    mock_result.meta = PaginationMeta(total=100)
    mock_client.repo.list.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn(offset=50, limit=25)

    assert result["success"] is True
    assert result["data"]["offset"] == 50
    assert result["data"]["limit"] == 25
    assert result["data"]["total"] == 100


@pytest.mark.asyncio
async def test_yuque_list_repos_limit_capped(mock_mcp, mock_client, sample_repo):
    """Test that limit is capped at 100."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = [sample_repo]
    mock_result.meta = PaginationMeta(total=200)
    mock_client.repo.list.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn(offset=0, limit=150)

    assert result["data"]["limit"] == 100  # Capped at 100
    mock_client.repo.list.assert_called_once_with(offset=0, limit=100)


@pytest.mark.asyncio
async def test_yuque_list_repos_empty(mock_mcp, mock_client):
    """Test listing repositories when empty."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = []
    mock_result.meta = PaginationMeta(total=0)
    mock_client.repo.list.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn()

    assert result["success"] is True
    assert result["data"]["repositories"] == []
    assert result["data"]["total"] == 0


@pytest.mark.asyncio
async def test_yuque_list_repos_without_meta(mock_mcp, mock_client, sample_repo):
    """Test listing repositories without meta data."""
    mock_result = MagicMock()
    mock_result.data = [sample_repo]
    mock_result.meta = None
    mock_client.repo.list.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn()

    assert result["data"]["total"] == 1  # Uses len(repos)


@pytest.mark.asyncio
async def test_yuque_list_repos_with_error(mock_mcp, mock_client):
    """Test listing repositories with error."""
    from yuque.exceptions import ServerError

    mock_client.repo.list.side_effect = ServerError("Server error")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    list_repos_tool = next(t for t in tools if t.name == "yuque_list_repos")

    result = await list_repos_tool.fn()

    assert result["success"] is False
    assert "Server error" in result["error"]
    assert "Failed to list repositories" in result["message"]


# ============================================
# Tool: yuque_get_user_repos
# ============================================


@pytest.mark.asyncio
async def test_yuque_get_user_repos_success(mock_mcp, mock_client, sample_repo):
    """Test getting user repositories successfully."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = [sample_repo]
    mock_result.meta = PaginationMeta(total=1)
    mock_client.repo.get_user_repos.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_user_repos_tool = next(t for t in tools if t.name == "yuque_get_user_repos")

    result = await get_user_repos_tool.fn(login="testuser")

    assert result["success"] is True
    assert result["data"]["user"] == "testuser"
    assert len(result["data"]["repositories"]) == 1
    assert result["data"]["total"] == 1
    mock_client.repo.get_user_repos.assert_called_once_with(login="testuser", offset=0, limit=100)


@pytest.mark.asyncio
async def test_yuque_get_user_repos_not_found(mock_mcp, mock_client):
    """Test getting repositories for non-existent user."""
    from yuque.exceptions import NotFoundError

    mock_client.repo.get_user_repos.side_effect = NotFoundError("User not found")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_user_repos_tool = next(t for t in tools if t.name == "yuque_get_user_repos")

    result = await get_user_repos_tool.fn(login="unknown")

    assert result["success"] is False
    assert "User not found" in result["error"]
    assert "Failed to get repositories for user unknown" in result["message"]


@pytest.mark.asyncio
async def test_yuque_get_user_repos_empty(mock_mcp, mock_client):
    """Test getting user repositories when empty."""
    from yuque.models import PaginationMeta

    mock_result = MagicMock()
    mock_result.data = []
    mock_result.meta = PaginationMeta(total=0)
    mock_client.repo.get_user_repos.return_value = mock_result

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_user_repos_tool = next(t for t in tools if t.name == "yuque_get_user_repos")

    result = await get_user_repos_tool.fn(login="testuser")

    assert result["success"] is True
    assert result["data"]["repositories"] == []


# ============================================
# Tool: yuque_get_group_repos
# ============================================


# ============================================
# Tool: yuque_get_repo_toc
# ============================================


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_success(mock_mcp, mock_client, sample_toc):
    """Test getting repository TOC successfully."""
    mock_client.repo.get_toc.return_value = sample_toc

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_tool = next(t for t in tools if t.name == "yuque_get_repo_toc")

    result = await get_toc_tool.fn(book_id=12345)

    assert result["success"] is True
    assert result["data"]["book_id"] == 12345
    assert result["data"]["total_items"] == 2
    assert len(result["data"]["toc"]) == 2
    mock_client.repo.get_toc.assert_called_once_with(book_id=12345)


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_nested_structure(mock_mcp, mock_client, sample_toc):
    """Test getting repository TOC with nested structure."""
    mock_client.repo.get_toc.return_value = sample_toc

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_tool = next(t for t in tools if t.name == "yuque_get_repo_toc")

    result = await get_toc_tool.fn(book_id=12345)

    # Check nested structure
    chapter1 = result["data"]["toc"][1]
    assert chapter1["title"] == "Chapter 1"
    assert "children" in chapter1
    assert len(chapter1["children"]) == 1

    # Check deeply nested
    section = chapter1["children"][0]
    assert section["title"] == "Section 1.1"
    assert "children" in section

    subsection = section["children"][0]
    assert subsection["title"] == "Subsection 1.1.1"
    assert subsection["depth"] == 3


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_empty(mock_mcp, mock_client):
    """Test getting repository TOC when empty."""
    mock_client.repo.get_toc.return_value = []

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_tool = next(t for t in tools if t.name == "yuque_get_repo_toc")

    result = await get_toc_tool.fn(book_id=12345)

    assert result["success"] is True
    assert result["data"]["toc"] == []
    assert result["data"]["total_items"] == 0


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_not_dict(mock_mcp, mock_client):
    """Test getting repository TOC when response is not a list."""
    mock_client.repo.get_toc.return_value = None

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_tool = next(t for t in tools if t.name == "yuque_get_repo_toc")

    result = await get_toc_tool.fn(book_id=12345)

    assert result["success"] is True
    assert result["data"]["toc"] == []
    assert result["data"]["total_items"] == 0


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_not_found(mock_mcp, mock_client):
    """Test getting TOC for non-existent repository."""
    from yuque.exceptions import NotFoundError

    mock_client.repo.get_toc.side_effect = NotFoundError("Repository not found")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_tool = next(t for t in tools if t.name == "yuque_get_repo_toc")

    result = await get_toc_tool.fn(book_id=999999)

    assert result["success"] is False
    assert "Repository not found" in result["error"]
    assert "Failed to get TOC for repository 999999" in result["message"]


# ============================================
# Tool: yuque_get_repo_toc_by_path
# ============================================


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_by_path_success(mock_mcp, mock_client, sample_toc):
    """Test getting repository TOC by path successfully."""
    mock_client.repo.get_toc_by_path.return_value = sample_toc

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_toc_by_path")

    result = await get_toc_by_path_tool.fn(group_login="testgroup", book_slug="test-repo")

    assert result["success"] is True
    assert result["data"]["path"] == "testgroup/test-repo"
    assert result["data"]["total_items"] == 2
    mock_client.repo.get_toc_by_path.assert_called_once_with(
        group_login="testgroup", book_slug="test-repo"
    )


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_by_path_nested(mock_mcp, mock_client, sample_toc):
    """Test getting repository TOC by path with nested structure."""
    mock_client.repo.get_toc_by_path.return_value = sample_toc

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_toc_by_path")

    result = await get_toc_by_path_tool.fn(group_login="eng", book_slug="docs")

    # Verify nested structure is preserved
    chapter1 = result["data"]["toc"][1]
    assert "children" in chapter1
    assert chapter1["children"][0]["title"] == "Section 1.1"


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_by_path_not_found(mock_mcp, mock_client):
    """Test getting TOC by non-existent path."""
    from yuque.exceptions import NotFoundError

    mock_client.repo.get_toc_by_path.side_effect = NotFoundError("Repository not found")

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_toc_by_path")

    result = await get_toc_by_path_tool.fn(group_login="unknown", book_slug="missing")

    assert result["success"] is False
    assert "Repository not found" in result["error"]
    assert "Failed to get TOC for repository unknown/missing" in result["message"]


@pytest.mark.asyncio
async def test_yuque_get_repo_toc_by_path_empty(mock_mcp, mock_client):
    """Test getting TOC by path when empty."""
    mock_client.repo.get_toc_by_path.return_value = []

    register_repo_tools(mock_mcp, mock_client)
    tools = list(mock_mcp._tool_manager._tools.values())
    get_toc_by_path_tool = next(t for t in tools if t.name == "yuque_get_repo_toc_by_path")

    result = await get_toc_by_path_tool.fn(group_login="testgroup", book_slug="empty-repo")

    assert result["success"] is True
    assert result["data"]["toc"] == []
    assert result["data"]["total_items"] == 0


# ============================================
# Tool Registration
# ============================================


def test_register_repo_tools(mock_mcp, mock_client):
    """Test that all repository tools are registered correctly."""
    register_repo_tools(mock_mcp, mock_client)

    tool_names = {tool.name for tool in mock_mcp._tool_manager._tools.values()}

    assert "yuque_get_repo" in tool_names
    assert "yuque_get_repo_by_path" in tool_names
    assert "yuque_list_repos" in tool_names
    assert "yuque_get_user_repos" in tool_names
    assert "yuque_get_repo_toc" in tool_names
    assert "yuque_get_repo_toc_by_path" in tool_names

    # Verify we have exactly 6 tools (removed yuque_get_group_repos - it's in group tools)
    assert len(mock_mcp._tool_manager._tools) == 6


def test_tool_descriptions(mock_mcp, mock_client):
    """Test that tools have proper descriptions."""
    register_repo_tools(mock_mcp, mock_client)

    for tool in mock_mcp._tool_manager._tools.values():
        assert tool.description is not None
        assert len(tool.description) > 10  # Ensure meaningful description
