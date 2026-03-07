"""Tests for Document MCP tools."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from yuque.mcp.tools.doc import (
    _format_doc,
    _format_doc_summary,
    _format_doc_version,
    _get_format_label,
    _get_public_label,
    register_doc_tools,
)
from yuque.models import (
    Document,
    DocumentVersion,
    Group,
    PaginatedResponse,
    PaginationMeta,
    Repository,
    User,
)


@pytest.fixture
def mock_client():
    """Create a mock YuqueClient."""
    client = MagicMock()
    client.doc = MagicMock()
    return client


@pytest.fixture
def sample_user():
    """Create a sample User instance."""
    return User(
        id=1001,
        login="testuser",
        name="Test User",
        email="test@example.com",
        avatar_url="https://example.com/avatar.png",
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        updated_at=datetime(2024, 1, 2, 15, 30, 0),
    )


@pytest.fixture
def sample_group():
    """Create a sample Group instance."""
    return Group(
        id=2001,
        login="testgroup",
        name="Test Group",
        description="Test group description",
        owner_id=1001,
        members_count=10,
        books_count=5,
    )


@pytest.fixture
def sample_repository(sample_user, sample_group):
    """Create a sample Repository instance."""
    return Repository(
        id=3001,
        type="Book",
        slug="test-repo",
        name="Test Repository",
        description="Test repository description",
        creator_id=1001,
        public=1,
        user=sample_user,
        group=sample_group,
    )


@pytest.fixture
def sample_document(sample_user, sample_repository):
    """Create a sample Document instance."""
    return {
        "id": 4001,
        "slug": "test-doc",
        "title": "Test Document",
        "body": "# Test Content\n\nThis is a test document.",
        "body_format": 1,
        "creator_id": 1001,
        "user_id": 1001,
        "book_id": 3001,
        "public": 0,
        "read_count": 100,
        "likes_count": 10,
        "comments_count": 5,
        "version": 3,
        "draft_version": 2,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-02T15:30:00Z",
        "published_at": "2024-01-01T11:00:00Z",
        "last_editor_id": 1001,
        "word_count": 150,
        "cover": "https://example.com/cover.png",
        "user": {
            "id": 1001,
            "login": "testuser",
            "name": "Test User",
        },
        "book": {
            "id": 3001,
            "name": "Test Repository",
            "slug": "test-repo",
        },
    }


@pytest.fixture
def sample_doc_summary():
    """Create a sample document summary dict."""
    return {
        "id": 4001,
        "slug": "test-doc",
        "title": "Test Document",
        "creator_id": 1001,
        "book_id": 3001,
        "public": 0,
        "read_count": 100,
        "likes_count": 10,
        "comments_count": 5,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-02T15:30:00Z",
        "user": {
            "id": 1001,
            "login": "testuser",
            "name": "Test User",
        },
    }


@pytest.fixture
def sample_doc_version():
    """Create a sample document version dict."""
    return {
        "id": 5001,
        "document_id": 4001,
        "content": "# Version 3\n\nUpdated content.",
        "description": "Fixed typo in introduction",
        "created_at": "2024-01-02T15:30:00Z",
    }


# ============================================================
# Helper Function Tests
# ============================================================


def test_format_doc(sample_document):
    """Test _format_doc helper function."""
    result = _format_doc(sample_document)

    assert result["id"] == 4001
    assert result["slug"] == "test-doc"
    assert result["title"] == "Test Document"
    assert result["body"] == "# Test Content\n\nThis is a test document."
    assert result["body_format"] == "markdown"
    assert result["creator_id"] == 1001
    assert result["user_id"] == 1001
    assert result["book_id"] == 3001
    assert result["public"] == "private"
    assert result["version"] == 3
    assert result["read_count"] == 100
    assert result["likes_count"] == 10
    assert result["comments_count"] == 5
    assert result["creator"]["name"] == "Test User"
    assert result["creator"]["login"] == "testuser"
    assert result["repository"]["name"] == "Test Repository"
    assert result["repository"]["slug"] == "test-repo"
    assert result["draft_version"] == 2
    assert result["last_editor_id"] == 1001
    assert result["word_count"] == 150
    assert result["cover"] == "https://example.com/cover.png"


def test_format_doc_minimal():
    """Test _format_doc with minimal data."""
    doc = {
        "id": 1,
        "slug": "minimal",
        "title": "Minimal Doc",
        "body_format": 1,
        "creator_id": 1,
        "user_id": 1,
        "book_id": 1,
    }
    result = _format_doc(doc)

    assert result["id"] == 1
    assert result["slug"] == "minimal"
    assert result["title"] == "Minimal Doc"
    assert result["body"] is None
    assert result["body_format"] == "markdown"
    assert result["public"] == "private"
    assert result["read_count"] == 0
    assert result["likes_count"] == 0
    assert result["comments_count"] == 0
    assert "creator" not in result
    assert "repository" not in result
    assert "draft_version" not in result


def test_format_doc_summary(sample_doc_summary):
    """Test _format_doc_summary helper function."""
    result = _format_doc_summary(sample_doc_summary)

    assert result["id"] == 4001
    assert result["slug"] == "test-doc"
    assert result["title"] == "Test Document"
    assert result["creator_id"] == 1001
    assert result["book_id"] == 3001
    assert result["public"] == "private"
    assert result["read_count"] == 100
    assert result["creator"]["name"] == "Test User"
    assert "body" not in result


def test_format_doc_summary_minimal():
    """Test _format_doc_summary with minimal data."""
    doc = {
        "id": 1,
        "slug": "minimal",
        "title": "Minimal Doc",
        "creator_id": 1,
        "book_id": 1,
    }
    result = _format_doc_summary(doc)

    assert result["id"] == 1
    assert result["slug"] == "minimal"
    assert result["title"] == "Minimal Doc"
    assert result["public"] == "private"
    assert "creator" not in result


def test_format_doc_version(sample_doc_version):
    """Test _format_doc_version helper function."""
    result = _format_doc_version(sample_doc_version)

    assert result["id"] == 5001
    assert result["document_id"] == 4001
    assert result["content"] == "# Version 3\n\nUpdated content."
    assert result["description"] == "Fixed typo in introduction"
    assert result["created_at"] == "2024-01-02T15:30:00Z"


def test_format_doc_version_minimal():
    """Test _format_doc_version with minimal data."""
    version = {
        "id": 1,
        "document_id": 1,
        "content": "Content",
        "created_at": "2024-01-01T00:00:00Z",
    }
    result = _format_doc_version(version)

    assert result["id"] == 1
    assert result["document_id"] == 1
    assert result["content"] == "Content"
    assert "description" not in result


def test_get_public_label():
    """Test _get_public_label helper function."""
    assert _get_public_label(0) == "private"
    assert _get_public_label(1) == "public"
    assert _get_public_label(2) == "enterprise-wide"
    assert _get_public_label(3) == "unknown (3)"
    assert _get_public_label(-1) == "unknown (-1)"


def test_get_format_label():
    """Test _get_format_label helper function."""
    assert _get_format_label(1) == "markdown"
    assert _get_format_label(2) == "html"
    assert _get_format_label(3) == "lake"
    assert _get_format_label(0) == "unknown (0)"
    assert _get_format_label(4) == "unknown (4)"


# ============================================================
# yuque_get_doc Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_doc_success(mock_client, sample_document):
    """Test getting document by ID successfully."""
    mock_client.doc.get.return_value = sample_document

    # Import and call the tool function directly
    from yuque.mcp.tools.doc import register_doc_tools
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    # Get the registered tool
    tool_func = mcp._tool_manager._tools["yuque_get_doc"].fn
    result = await tool_func(doc_id=4001)

    assert result["success"] is True
    assert "data" in result
    assert result["data"]["id"] == 4001
    assert result["data"]["title"] == "Test Document"
    mock_client.doc.get.assert_called_once_with(doc_id=4001)


@pytest.mark.asyncio
async def test_get_doc_not_found(mock_client):
    """Test getting non-existent document."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.get.side_effect = NotFoundError("Document not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_doc"].fn
    result = await tool_func(doc_id=999999)

    assert result["success"] is False
    assert "error" in result
    assert "message" in result
    assert "Document not found" in result["error"]


@pytest.mark.asyncio
async def test_get_doc_permission_denied(mock_client):
    """Test getting document without permission."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.doc.get.side_effect = PermissionDeniedError("Access denied")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_doc"].fn
    result = await tool_func(doc_id=4001)

    assert result["success"] is False
    assert "Access denied" in result["error"]


# ============================================================
# yuque_get_docs_by_repo Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_docs_by_repo_success(mock_client, sample_doc_summary):
    """Test getting documents by repository successfully."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary, sample_doc_summary],
        meta=PaginationMeta(page=1, per_page=20, total=2, total_pages=1),
    )
    mock_client.doc.get_by_repo.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_repo"].fn
    result = await tool_func(book_id=3001, offset=0, limit=20)

    assert result["success"] is True
    assert result["data"]["book_id"] == 3001
    assert len(result["data"]["documents"]) == 2
    assert result["data"]["total"] == 2
    assert result["data"]["offset"] == 0
    assert result["data"]["limit"] == 20
    mock_client.doc.get_by_repo.assert_called_once_with(book_id=3001, offset=0, limit=20)


@pytest.mark.asyncio
async def test_get_docs_by_repo_pagination_limit(mock_client, sample_doc_summary):
    """Test that limit is capped at 100."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary],
        meta=PaginationMeta(page=1, per_page=100, total=1, total_pages=1),
    )
    mock_client.doc.get_by_repo.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_repo"].fn
    result = await tool_func(book_id=3001, offset=0, limit=150)

    # Verify limit is capped at 100
    mock_client.doc.get_by_repo.assert_called_once_with(book_id=3001, offset=0, limit=100)
    assert result["data"]["limit"] == 100


@pytest.mark.asyncio
async def test_get_docs_by_repo_empty(mock_client):
    """Test getting documents from empty repository."""
    paginated_response = PaginatedResponse(
        data=[],
        meta=PaginationMeta(page=1, per_page=20, total=0, total_pages=0),
    )
    mock_client.doc.get_by_repo.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_repo"].fn
    result = await tool_func(book_id=3001)

    assert result["success"] is True
    assert len(result["data"]["documents"]) == 0
    assert result["data"]["total"] == 0


@pytest.mark.asyncio
async def test_get_docs_by_repo_error(mock_client):
    """Test getting documents with error."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.get_by_repo.side_effect = NotFoundError("Repository not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_repo"].fn
    result = await tool_func(book_id=999999)

    assert result["success"] is False
    assert "Repository not found" in result["error"]


# ============================================================
# yuque_get_docs_by_path Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_docs_by_path_success(mock_client, sample_doc_summary):
    """Test getting documents by path successfully."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.doc.get_by_path.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_path"].fn
    result = await tool_func(group_login="testgroup", book_slug="test-repo", offset=0, limit=20)

    assert result["success"] is True
    assert result["data"]["path"] == "testgroup/test-repo"
    assert len(result["data"]["documents"]) == 1
    assert result["data"]["total"] == 1
    mock_client.doc.get_by_path.assert_called_once_with(
        group_login="testgroup", book_slug="test-repo", offset=0, limit=20
    )


@pytest.mark.asyncio
async def test_get_docs_by_path_pagination_limit(mock_client, sample_doc_summary):
    """Test that limit is capped at 100 for path-based query."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary],
        meta=PaginationMeta(page=1, per_page=100, total=1, total_pages=1),
    )
    mock_client.doc.get_by_path.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_path"].fn
    result = await tool_func(group_login="testgroup", book_slug="test-repo", limit=200)

    mock_client.doc.get_by_path.assert_called_once_with(
        group_login="testgroup", book_slug="test-repo", offset=0, limit=100
    )
    assert result["data"]["limit"] == 100


@pytest.mark.asyncio
async def test_get_docs_by_path_error(mock_client):
    """Test getting documents by path with error."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.get_by_path.side_effect = NotFoundError("Path not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_path"].fn
    result = await tool_func(group_login="invalid", book_slug="invalid")

    assert result["success"] is False
    assert "Path not found" in result["error"]


# ============================================================
# yuque_create_doc Tests
# ============================================================


@pytest.mark.asyncio
async def test_create_doc_success(mock_client, sample_document):
    """Test creating document successfully."""
    mock_client.doc.create.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_create_doc"].fn
    result = await tool_func(
        book_id=3001,
        title="Test Document",
        slug="test-doc",
        body="# Test Content",
        format="markdown",
        public=0,
    )

    assert result["success"] is True
    assert result["data"]["id"] == 4001
    assert result["data"]["title"] == "Test Document"
    assert "created successfully" in result["message"]
    mock_client.doc.create.assert_called_once_with(
        book_id=3001,
        title="Test Document",
        slug="test-doc",
        body="# Test Content",
        format="markdown",
        public=0,
    )


@pytest.mark.asyncio
async def test_create_doc_default_values(mock_client, sample_document):
    """Test creating document with default values."""
    mock_client.doc.create.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_create_doc"].fn
    result = await tool_func(book_id=3001)

    assert result["success"] is True
    mock_client.doc.create.assert_called_once_with(
        book_id=3001,
        title="无标题",
        slug=None,
        body=None,
        format="markdown",
        public=0,
    )


@pytest.mark.asyncio
async def test_create_doc_permission_denied(mock_client):
    """Test creating document without permission."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.doc.create.side_effect = PermissionDeniedError("No write permission")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_create_doc"].fn
    result = await tool_func(book_id=3001, title="Test")

    assert result["success"] is False
    assert "No write permission" in result["error"]


# ============================================================
# yuque_create_doc_by_path Tests
# ============================================================


@pytest.mark.asyncio
async def test_create_doc_by_path_success(mock_client, sample_document):
    """Test creating document by path successfully."""
    mock_client.doc.create_by_path.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_create_doc_by_path"].fn
    result = await tool_func(
        group_login="testgroup",
        book_slug="test-repo",
        title="Test Document",
        body="# Content",
    )

    assert result["success"] is True
    assert result["data"]["id"] == 4001
    assert "testgroup/test-repo" in result["message"]
    mock_client.doc.create_by_path.assert_called_once()


@pytest.mark.asyncio
async def test_create_doc_by_path_error(mock_client):
    """Test creating document by path with error."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.create_by_path.side_effect = NotFoundError("Repository not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_create_doc_by_path"].fn
    result = await tool_func(group_login="invalid", book_slug="invalid", title="Test")

    assert result["success"] is False
    assert "Repository not found" in result["error"]


# ============================================================
# yuque_update_doc Tests
# ============================================================


@pytest.mark.asyncio
async def test_update_doc_success(mock_client, sample_document):
    """Test updating document successfully."""
    mock_client.doc.update.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_update_doc"].fn
    result = await tool_func(
        doc_id=4001,
        title="Updated Title",
        body="Updated content",
        format="markdown",
        public=1,
    )

    assert result["success"] is True
    assert result["data"]["id"] == 4001
    assert "updated successfully" in result["message"]
    mock_client.doc.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_doc_partial(mock_client, sample_document):
    """Test updating document with partial data."""
    mock_client.doc.update.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_update_doc"].fn
    result = await tool_func(doc_id=4001, title="New Title")

    assert result["success"] is True
    mock_client.doc.update.assert_called_once_with(
        doc_id=4001,
        title="New Title",
        slug=None,
        body=None,
        format="markdown",
        public=0,
    )


@pytest.mark.asyncio
async def test_update_doc_not_found(mock_client):
    """Test updating non-existent document."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.update.side_effect = NotFoundError("Document not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_update_doc"].fn
    result = await tool_func(doc_id=999999, title="Test")

    assert result["success"] is False
    assert "Document not found" in result["error"]


# ============================================================
# yuque_update_doc_by_repo Tests
# ============================================================


@pytest.mark.asyncio
async def test_update_doc_by_repo_success(mock_client, sample_document):
    """Test updating document in repository successfully."""
    mock_client.doc.update_by_repo.return_value = sample_document

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_update_doc_by_repo"].fn
    result = await tool_func(
        book_id=3001,
        doc_id=4001,
        title="Updated Title",
        body="Updated content",
    )

    assert result["success"] is True
    assert result["data"]["id"] == 4001
    assert "repository 3001" in result["message"]
    mock_client.doc.update_by_repo.assert_called_once()


@pytest.mark.asyncio
async def test_update_doc_by_repo_error(mock_client):
    """Test updating document in repository with error."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.doc.update_by_repo.side_effect = PermissionDeniedError("No permission")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_update_doc_by_repo"].fn
    result = await tool_func(book_id=3001, doc_id=4001, title="Test")

    assert result["success"] is False
    assert "No permission" in result["error"]


# ============================================================
# yuque_delete_doc Tests
# ============================================================


@pytest.mark.asyncio
async def test_delete_doc_success(mock_client):
    """Test deleting document successfully."""
    mock_client.doc.delete.return_value = None

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_delete_doc"].fn
    result = await tool_func(doc_id=4001)

    assert result["success"] is True
    assert result["data"]["doc_id"] == 4001
    assert result["data"]["deleted"] is True
    assert "deleted successfully" in result["message"]
    mock_client.doc.delete.assert_called_once_with(doc_id=4001)


@pytest.mark.asyncio
async def test_delete_doc_not_found(mock_client):
    """Test deleting non-existent document."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.delete.side_effect = NotFoundError("Document not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_delete_doc"].fn
    result = await tool_func(doc_id=999999)

    assert result["success"] is False
    assert "Document not found" in result["error"]


@pytest.mark.asyncio
async def test_delete_doc_permission_denied(mock_client):
    """Test deleting document without permission."""
    from yuque.exceptions import PermissionDeniedError

    mock_client.doc.delete.side_effect = PermissionDeniedError("Cannot delete")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_delete_doc"].fn
    result = await tool_func(doc_id=4001)

    assert result["success"] is False
    assert "Cannot delete" in result["error"]


# ============================================================
# yuque_get_doc_version Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_doc_version_success(mock_client, sample_doc_version):
    """Test getting document version successfully."""
    mock_client.doc.get_version.return_value = sample_doc_version

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_doc_version"].fn
    result = await tool_func(version_id=5001)

    assert result["success"] is True
    assert result["data"]["id"] == 5001
    assert result["data"]["document_id"] == 4001
    assert result["data"]["description"] == "Fixed typo in introduction"
    mock_client.doc.get_version.assert_called_once_with(version_id=5001)


@pytest.mark.asyncio
async def test_get_doc_version_not_found(mock_client):
    """Test getting non-existent version."""
    from yuque.exceptions import NotFoundError

    mock_client.doc.get_version.side_effect = NotFoundError("Version not found")

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_doc_version"].fn
    result = await tool_func(version_id=999999)

    assert result["success"] is False
    assert "Version not found" in result["error"]


# ============================================================
# Tool Registration Tests
# ============================================================


def test_register_doc_tools():
    """Test that all document tools are registered correctly."""
    from mcp.server.fastmcp import FastMCP

    mock_client = MagicMock()
    mcp = FastMCP("test")

    register_doc_tools(mcp, mock_client)

    # Verify all 9 tools are registered
    assert len(mcp._tool_manager._tools) == 9
    tool_names = {tool.name for tool in mcp._tool_manager._tools.values()}

    expected_tools = {
        "yuque_get_doc",
        "yuque_get_docs_by_repo",
        "yuque_get_docs_by_path",
        "yuque_create_doc",
        "yuque_create_doc_by_path",
        "yuque_update_doc",
        "yuque_update_doc_by_repo",
        "yuque_delete_doc",
        "yuque_get_doc_version",
    }

    assert tool_names == expected_tools


def test_register_doc_tools_with_mcp():
    """Test that tools can be registered with MCP server."""
    from mcp.server.fastmcp import FastMCP

    mock_client = MagicMock()
    mcp = FastMCP("test-yuque")

    # Register tools
    register_doc_tools(mcp, mock_client)

    # Verify tools are accessible
    tools = list(mcp._tool_manager._tools.values())
    assert len(tools) == 9

    # Verify tool descriptions exist
    for tool in tools:
        assert tool.description is not None
        assert len(tool.description) > 0


# ============================================================
# Edge Cases and Error Handling Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_docs_by_repo_without_meta(mock_client, sample_doc_summary):
    """Test getting documents when meta is None."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary],
        meta=None,
    )
    mock_client.doc.get_by_repo.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_repo"].fn
    result = await tool_func(book_id=3001)

    assert result["success"] is True
    # When meta is None, total should equal len(docs)
    assert result["data"]["total"] == 1


@pytest.mark.asyncio
async def test_get_docs_by_path_without_meta(mock_client, sample_doc_summary):
    """Test getting documents by path when meta is None."""
    paginated_response = PaginatedResponse(
        data=[sample_doc_summary],
        meta=None,
    )
    mock_client.doc.get_by_path.return_value = paginated_response

    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("test")
    register_doc_tools(mcp, mock_client)

    tool_func = mcp._tool_manager._tools["yuque_get_docs_by_path"].fn
    result = await tool_func(group_login="testgroup", book_slug="test-repo")

    assert result["success"] is True
    assert result["data"]["total"] == 1


@pytest.mark.asyncio
async def test_format_doc_with_public_levels():
    """Test formatting documents with different public levels."""
    from mcp.server.fastmcp import FastMCP

    # Test each public level
    for public_level, expected_label in [(0, "private"), (1, "public"), (2, "enterprise-wide")]:
        mock_client = MagicMock()
        doc = {
            "id": 1,
            "slug": "test",
            "title": "Test",
            "body_format": 1,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 1,
            "public": public_level,
        }
        mock_client.doc.get.return_value = doc

        mcp = FastMCP("test")
        register_doc_tools(mcp, mock_client)

        tool_func = mcp._tool_manager._tools["yuque_get_doc"].fn
        result = await tool_func(doc_id=1)

        assert result["success"] is True
        assert result["data"]["public"] == expected_label


@pytest.mark.asyncio
async def test_format_doc_with_different_formats():
    """Test formatting documents with different body formats."""
    from mcp.server.fastmcp import FastMCP

    # Test each body format
    for body_format, expected_label in [(1, "markdown"), (2, "html"), (3, "lake")]:
        mock_client = MagicMock()
        doc = {
            "id": 1,
            "slug": "test",
            "title": "Test",
            "body_format": body_format,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 1,
        }
        mock_client.doc.get.return_value = doc

        mcp = FastMCP("test")
        register_doc_tools(mcp, mock_client)

        tool_func = mcp._tool_manager._tools["yuque_get_doc"].fn
        result = await tool_func(doc_id=1)

        assert result["success"] is True
        assert result["data"]["body_format"] == expected_label
