"""Tests for DocAPI class."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from yuque.api.doc import DocAPI
from yuque.models import PaginatedResponse


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock(return_value={"data": {}})
    client._request_async = AsyncMock(return_value={"data": {}})
    return client


@pytest.fixture
def doc_api(mock_client):
    return DocAPI(mock_client)


@pytest.fixture
def sample_doc_data():
    return {
        "id": 12345,
        "slug": "test-doc",
        "title": "Test Document",
        "body": "# Test Content",
        "body_format": 1,
        "creator_id": 100,
        "user_id": 100,
        "book_id": 200,
        "public": 0,
        "read_count": 10,
        "likes_count": 5,
        "comments_count": 2,
        "version": 1,
    }


class TestDocAPIGet:
    def test_get(self, doc_api, mock_client, sample_doc_data):
        doc_id = 12345
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.get(doc_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/docs/{doc_id}", None, None
        )
        assert result == sample_doc_data

    def test_get_by_repo(self, doc_api, mock_client):
        book_id = 200
        docs_data = [{"id": 1, "title": "Doc 1"}, {"id": 2, "title": "Doc 2"}]
        mock_client._request.return_value = {
            "data": docs_data,
            "meta": {"page": 1, "per_page": 100, "total": 2, "total_pages": 1},
        }

        result = doc_api.get_by_repo(book_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{book_id}/docs", {"offset": 0, "limit": 100}, None
        )
        assert isinstance(result, PaginatedResponse)
        assert result.data == docs_data

    def test_get_by_repo_with_pagination(self, doc_api, mock_client):
        book_id = 200
        offset = 10
        limit = 20
        docs_data = [{"id": 3, "title": "Doc 3"}]
        mock_client._request.return_value = {"data": docs_data}

        result = doc_api.get_by_repo(book_id, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{book_id}/docs", {"offset": offset, "limit": limit}, None
        )
        assert result.data == docs_data

    def test_get_by_path(self, doc_api, mock_client):
        group_login = "my-group"
        book_slug = "my-book"
        docs_data = [{"id": 1, "title": "Doc 1"}]
        mock_client._request.return_value = {"data": docs_data}

        result = doc_api.get_by_path(group_login, book_slug)

        mock_client._request.assert_called_once_with(
            "GET",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            {"offset": 0, "limit": 100},
            None,
        )
        assert result.data == docs_data

    def test_get_by_path_with_pagination(self, doc_api, mock_client):
        group_login = "my-group"
        book_slug = "my-book"
        offset = 5
        limit = 10
        docs_data = [{"id": 2, "title": "Doc 2"}]
        mock_client._request.return_value = {"data": docs_data}

        result = doc_api.get_by_path(group_login, book_slug, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET",
            f"/api/v2/repos/{group_login}/{book_slug}/docs",
            {"offset": offset, "limit": limit},
            None,
        )
        assert result.data == docs_data

    def test_get_doc_by_path(self, doc_api, mock_client, sample_doc_data):
        namespace = "my-group/my-book"
        slug = "test-doc"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.get_doc_by_path(namespace, slug)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{namespace}/docs/{slug}", None, None
        )
        assert result == sample_doc_data

    def test_get_doc_by_path_with_raw(self, doc_api, mock_client, sample_doc_data):
        namespace = "my-group/my-book"
        slug = "test-doc"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.get_doc_by_path(namespace, slug, raw=True)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{namespace}/docs/{slug}", {"raw": 1}, None
        )
        assert result == sample_doc_data

    @pytest.mark.asyncio
    async def test_get_doc_by_path_async(self, doc_api, mock_client, sample_doc_data):
        namespace = "my-group/my-book"
        slug = "test-doc"
        mock_client._request_async.return_value = {"data": sample_doc_data}

        result = await doc_api.get_doc_by_path_async(namespace, slug)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/repos/{namespace}/docs/{slug}", None, None
        )
        assert result == sample_doc_data

    def test_get_version(self, doc_api, mock_client):
        version_id = 1
        version_data = {"id": 1, "content": "Version 1 content"}
        mock_client._request.return_value = {"data": version_data}

        result = doc_api.get_version(version_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/doc_versions/{version_id}", None, None
        )
        assert result == version_data


class TestDocAPICreate:
    def test_create(self, doc_api, mock_client, sample_doc_data):
        book_id = 200
        title = "New Doc"
        body = "# Content"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.create(book_id, title=title, body=body)

        expected_data = {
            "title": title,
            "slug": None,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request.assert_called_once_with(
            "POST", f"/api/v2/repos/{book_id}/docs", None, expected_data
        )
        assert result == sample_doc_data

    def test_create_with_all_params(self, doc_api, mock_client, sample_doc_data):
        book_id = 200
        title = "Full Doc"
        slug = "full-doc"
        body = "# Full Content"
        format_type = "markdown"
        public = 1
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.create(
            book_id, title=title, slug=slug, body=body, format=format_type, public=public
        )

        expected_data = {
            "title": title,
            "slug": slug,
            "body": body,
            "format": format_type,
            "public": public,
        }
        mock_client._request.assert_called_once_with(
            "POST", f"/api/v2/repos/{book_id}/docs", None, expected_data
        )
        assert result == sample_doc_data

    def test_create_by_path(self, doc_api, mock_client, sample_doc_data):
        group_login = "my-group"
        book_slug = "my-book"
        title = "New Doc"
        body = "# Content"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.create_by_path(group_login, book_slug, title=title, body=body)

        expected_data = {
            "title": title,
            "slug": None,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request.assert_called_once_with(
            "POST", f"/api/v2/repos/{group_login}/{book_slug}/docs", None, expected_data
        )
        assert result == sample_doc_data


class TestDocAPIUpdate:
    def test_update(self, doc_api, mock_client, sample_doc_data):
        book_id = 200
        doc_id = 12345
        title = "Updated Title"
        body = "Updated content"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.update(book_id, doc_id, title=title, body=body)

        expected_data = {
            "title": title,
            "slug": None,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}/docs/{doc_id}", None, expected_data
        )
        assert result == sample_doc_data

    def test_update_by_repo(self, doc_api, mock_client, sample_doc_data):
        book_id = 200
        doc_id = 12345
        title = "Updated Title"
        body = "Updated content"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.update_by_repo(book_id, doc_id, title=title, body=body)

        expected_data = {
            "title": title,
            "slug": None,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}/docs/{doc_id}", None, expected_data
        )
        assert result == sample_doc_data

    def test_update_by_path(self, doc_api, mock_client, sample_doc_data):
        namespace = "my-group/my-book"
        slug = "test-doc"
        title = "Updated Title"
        body = "Updated content"
        mock_client._request.return_value = {"data": sample_doc_data}

        result = doc_api.update_by_path(namespace, slug, title=title, body=body)

        expected_data = {
            "title": title,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{namespace}/docs/{slug}", None, expected_data
        )
        assert result == sample_doc_data

    @pytest.mark.asyncio
    async def test_update_by_path_async(self, doc_api, mock_client, sample_doc_data):
        namespace = "my-group/my-book"
        slug = "test-doc"
        title = "Updated Title"
        body = "Updated content"
        mock_client._request_async.return_value = {"data": sample_doc_data}

        result = await doc_api.update_by_path_async(namespace, slug, title=title, body=body)

        expected_data = {
            "title": title,
            "body": body,
            "format": "markdown",
            "public": 0,
        }
        mock_client._request_async.assert_called_once_with(
            "PUT", f"/api/v2/repos/{namespace}/docs/{slug}", None, expected_data
        )
        assert result == sample_doc_data


class TestDocAPIDelete:
    def test_delete(self, doc_api, mock_client):
        book_id = 200
        doc_id = 12345
        mock_client._request.return_value = {"data": {"success": True}}

        result = doc_api.delete(book_id, doc_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{book_id}/docs/{doc_id}", None, None
        )
        assert result == {"success": True}

    def test_delete_no_data(self, doc_api, mock_client):
        book_id = 200
        doc_id = 12345
        mock_client._request.return_value = {}

        result = doc_api.delete(book_id, doc_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{book_id}/docs/{doc_id}", None, None
        )
        assert result == {}

    def test_delete_by_path(self, doc_api, mock_client):
        namespace = "my-group/my-book"
        slug = "test-doc"
        mock_client._request.return_value = {"data": {"success": True}}

        result = doc_api.delete_by_path(namespace, slug)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{namespace}/docs/{slug}", None, None
        )
        assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_delete_by_path_async(self, doc_api, mock_client):
        namespace = "my-group/my-book"
        slug = "test-doc"
        mock_client._request_async.return_value = {"data": {"success": True}}

        result = await doc_api.delete_by_path_async(namespace, slug)

        mock_client._request_async.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{namespace}/docs/{slug}", None, None
        )
        assert result == {"success": True}
