"""Tests for Search MCP tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from yuque.mcp.tools.search import (
    register_search_tools,
    search_content,
)
from yuque.models import PaginatedResponse, PaginationMeta, Repository, SearchResult, User


@pytest.fixture
def mock_client():
    """Create a mock YuqueClient."""
    client = MagicMock()
    client.search = MagicMock()
    client.search.search_async = AsyncMock()
    return client


@pytest.fixture
def sample_user():
    """Create a sample User instance."""
    return User(
        id=100,
        login="author",
        name="Author Name",
        avatar_url="https://example.com/avatar.png",
    )


@pytest.fixture
def sample_book():
    """Create a sample Repository instance."""
    return Repository(
        id=200,
        type="Book",
        name="API Documentation",
        slug="api-docs",
        description="API reference docs",
        creator_id=100,
        public=1,
    )


@pytest.fixture
def sample_doc_result(sample_user, sample_book):
    """Create a sample document search result."""
    return SearchResult(
        id=12345,
        type="doc",
        title="Python API Guide",
        summary="A comprehensive guide to using Python APIs effectively and efficiently.",
        url="https://www.yuque.com/test/api-docs/python-guide",
        user=sample_user,
        book=sample_book,
    )


@pytest.fixture
def sample_book_result(sample_user):
    """Create a sample book search result."""
    return SearchResult(
        id=200,
        type="book",
        title="Engineering Handbook",
        summary="Team engineering practices and standards.",
        url="https://www.yuque.com/engineering/handbook",
        user=sample_user,
        book=None,
    )


@pytest.fixture
def sample_user_result():
    """Create a sample user search result."""
    return SearchResult(
        id=300,
        type="user",
        title="John Doe",
        summary="Senior Engineer",
        url="https://www.yuque.com/johndoe",
        user=User(id=300, login="johndoe", name="John Doe"),
        book=None,
    )


@pytest.fixture
def sample_group_result():
    """Create a sample group search result."""
    return SearchResult(
        id=400,
        type="group",
        title="Engineering Team",
        summary="Product engineering team workspace",
        url="https://www.yuque.com/engineering",
        user=None,
        book=None,
    )


@pytest.mark.asyncio
async def test_search_docs_success(mock_client, sample_doc_result):
    """Test searching for documents successfully."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="python", type="doc", page=1)

    assert "# Search Results for 'python'" in result
    assert "**Type**: doc" in result
    assert "**Page**: 1" in result
    assert "**Total Results**: 1" in result
    assert "Python API Guide" in result
    assert "12345" in result
    mock_client.search.search_async.assert_called_once_with(keyword="python", type="doc", page=1)


@pytest.mark.asyncio
async def test_search_books_success(mock_client, sample_book_result):
    """Test searching for books/repositories successfully."""
    mock_response = PaginatedResponse(
        data=[sample_book_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="handbook", type="book")

    assert "# Search Results for 'handbook'" in result
    assert "**Type**: book" in result
    assert "Engineering Handbook" in result
    mock_client.search.search_async.assert_called_once_with(keyword="handbook", type="book", page=1)


@pytest.mark.asyncio
async def test_search_users_success(mock_client, sample_user_result):
    """Test searching for users successfully."""
    mock_response = PaginatedResponse(
        data=[sample_user_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="john", type="user")

    assert "# Search Results for 'john'" in result
    assert "**Type**: user" in result
    assert "John Doe" in result
    mock_client.search.search_async.assert_called_once_with(keyword="john", type="user", page=1)


@pytest.mark.asyncio
async def test_search_groups_success(mock_client, sample_group_result):
    """Test searching for groups successfully."""
    mock_response = PaginatedResponse(
        data=[sample_group_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="engineering", type="group")

    assert "# Search Results for 'engineering'" in result
    assert "**Type**: group" in result
    assert "Engineering Team" in result
    mock_client.search.search_async.assert_called_once_with(
        keyword="engineering", type="group", page=1
    )


@pytest.mark.asyncio
async def test_search_invalid_type(mock_client):
    """Test search with invalid type parameter."""
    result = await search_content(mock_client, keyword="test", type="invalid")

    assert "Invalid type 'invalid'" in result
    assert "Must be one of" in result
    assert "book" in result or "doc" in result
    mock_client.search.search_async.assert_not_called()


@pytest.mark.asyncio
async def test_search_empty_results(mock_client):
    """Test search with no results found."""
    mock_response = PaginatedResponse(
        data=[],
        meta=PaginationMeta(page=1, per_page=20, total=0, total_pages=0),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="nonexistent")

    assert "No results found" in result
    assert "**Tips**:" in result
    assert "Try different keywords" in result


@pytest.mark.asyncio
async def test_search_with_pagination(mock_client, sample_doc_result):
    """Test search with pagination parameters."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result],
        meta=PaginationMeta(page=2, per_page=20, total=50, total_pages=3),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="api", type="doc", page=2)

    assert "**Page**: 2" in result
    assert "**Total Results**: 50" in result
    assert "**Total Pages**: 3" in result
    assert "Previous page: Use `page=1`" in result
    assert "Next page: Use `page=3`" in result
    mock_client.search.search_async.assert_called_once_with(keyword="api", type="doc", page=2)


@pytest.mark.asyncio
async def test_search_pagination_first_page(mock_client, sample_doc_result):
    """Test pagination hints on first page."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result],
        meta=PaginationMeta(page=1, per_page=20, total=50, total_pages=3),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="test", page=1)

    assert "Previous page" not in result  # No previous on first page
    assert "Next page: Use `page=2`" in result


@pytest.mark.asyncio
async def test_search_pagination_last_page(mock_client, sample_doc_result):
    """Test pagination hints on last page."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result],
        meta=PaginationMeta(page=3, per_page=20, total=50, total_pages=3),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="test", page=3)

    assert "Previous page: Use `page=2`" in result
    assert "Next page" not in result  # No next on last page


@pytest.mark.asyncio
async def test_search_markdown_formatting(mock_client, sample_doc_result):
    """Test markdown formatting of search results."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="python")

    assert "## 1. Python API Guide" in result
    assert "- **ID**: 12345" in result
    assert "- **Type**: doc" in result
    assert "- **Summary**:" in result
    assert "- **URL**:" in result
    assert "- **Author**:" in result
    assert "- **Repository**:" in result


@pytest.mark.asyncio
async def test_search_summary_truncation(mock_client):
    """Test that long summaries are truncated."""
    long_summary = "A" * 300  # 300 chars, should be truncated to 200
    long_result = SearchResult(
        id=1,
        type="doc",
        title="Long Summary Doc",
        summary=long_summary,
        url="https://example.com",
    )
    mock_response = PaginatedResponse(
        data=[long_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="test")

    assert "..." in result
    assert "- **Summary**:" in result


@pytest.mark.asyncio
async def test_search_result_without_optional_fields(mock_client):
    """Test search result without optional fields like summary, URL."""
    minimal_result = SearchResult(
        id=1,
        type="doc",
        title="Minimal Doc",
        summary=None,
        url=None,
    )
    mock_response = PaginatedResponse(
        data=[minimal_result],
        meta=PaginationMeta(page=1, per_page=20, total=1, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="test")

    assert "Minimal Doc" in result
    assert "- **ID**: 1" in result


@pytest.mark.asyncio
async def test_search_multiple_results(mock_client, sample_doc_result, sample_book_result):
    """Test search with multiple results."""
    mock_response = PaginatedResponse(
        data=[sample_doc_result, sample_book_result],
        meta=PaginationMeta(page=1, per_page=20, total=2, total_pages=1),
    )
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="guide")

    assert "Found 2 result(s)" in result
    assert "## 1." in result
    assert "## 2." in result


@pytest.mark.asyncio
async def test_search_with_error(mock_client):
    """Test search with API error."""
    from yuque.exceptions import AuthenticationError

    mock_client.search.search_async.side_effect = AuthenticationError("Invalid token")

    result = await search_content(mock_client, keyword="test")

    assert "Error searching for 'test'" in result
    assert "Invalid token" in result


@pytest.mark.asyncio
async def test_search_with_rate_limit_error(mock_client):
    """Test search with rate limit error."""
    from yuque.exceptions import RateLimitError

    mock_client.search.search_async.side_effect = RateLimitError("Rate limit exceeded")

    result = await search_content(mock_client, keyword="api")

    assert "Error searching for 'api'" in result
    assert "Rate limit exceeded" in result


@pytest.mark.asyncio
async def test_search_with_network_error(mock_client):
    """Test search with network error."""
    from yuque.exceptions import NetworkError

    mock_client.search.search_async.side_effect = NetworkError("Connection failed")

    result = await search_content(mock_client, keyword="test")

    assert "Error searching for 'test'" in result
    assert "Connection failed" in result


@pytest.mark.asyncio
async def test_search_without_meta(mock_client, sample_doc_result):
    """Test search response without pagination metadata."""
    mock_response = PaginatedResponse(data=[sample_doc_result], meta=None)
    mock_client.search.search_async.return_value = mock_response

    result = await search_content(mock_client, keyword="test")

    assert "# Search Results for 'test'" in result
    assert "Python API Guide" in result
    assert "Total Results" not in result


def test_register_search_tools():
    """Test that search tools are registered correctly."""
    from mcp.server.fastmcp import FastMCP

    mock_client = MagicMock()
    mcp = FastMCP("test")

    register_search_tools(mcp, mock_client)

    assert len(mcp._tool_manager._tools) == 1
    tool_names = {tool.name for tool in mcp._tool_manager._tools.values()}
    assert "yuque_search" in tool_names
