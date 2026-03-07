"""Tests for RepoAPI class."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from yuque.api.repo import RepoAPI
from yuque.models import PaginatedResponse


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock(return_value={"data": {}})
    client._request_async = AsyncMock(return_value={"data": {}})
    client.user = Mock()
    client.user.get_me = Mock(return_value=Mock(login="testuser"))
    client.user.get_me_async = AsyncMock(return_value=Mock(login="testuser"))
    return client


@pytest.fixture
def repo_api(mock_client):
    return RepoAPI(mock_client)


@pytest.fixture
def sample_repo_data():
    return {
        "id": 200,
        "type": "Book",
        "slug": "test-repo",
        "name": "Test Repository",
        "description": "Test repository description",
        "creator_id": 100,
        "public": 0,
        "has_toc": True,
    }


class TestRepoAPIGet:
    def test_get(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.get(book_id)

        mock_client._request.assert_called_once_with("GET", f"/api/v2/repos/{book_id}", None, None)
        assert result == sample_repo_data

    def test_get_by_path(self, repo_api, mock_client, sample_repo_data):
        group_login = "my-group"
        book_slug = "my-book"
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.get_by_path(group_login, book_slug)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{group_login}/{book_slug}", None, None
        )
        assert result == sample_repo_data

    def test_list(self, repo_api, mock_client):
        repos_data = [{"id": 1, "name": "Repo 1"}, {"id": 2, "name": "Repo 2"}]
        mock_client._request.return_value = {
            "data": repos_data,
            "meta": {"page": 1, "per_page": 100, "total": 2, "total_pages": 1},
        }
        mock_client.user.get_me.return_value = Mock(login="testuser")

        result = repo_api.list()

        mock_client.user.get_me.assert_called_once()
        mock_client._request.assert_called_once_with(
            "GET", "/api/v2/users/testuser/repos", {"offset": 0, "limit": 100}, None
        )
        assert isinstance(result, PaginatedResponse)
        assert result.data == repos_data

    def test_list_with_pagination(self, repo_api, mock_client):
        offset = 10
        limit = 20
        repos_data = [{"id": 3, "name": "Repo 3"}]
        mock_client._request.return_value = {"data": repos_data}
        mock_client.user.get_me.return_value = Mock(login="testuser")

        result = repo_api.list(offset=offset, limit=limit)

        mock_client.user.get_me.assert_called_once()
        mock_client._request.assert_called_once_with(
            "GET", "/api/v2/users/testuser/repos", {"offset": offset, "limit": limit}, None
        )
        assert result.data == repos_data

    def test_get_user_repos(self, repo_api, mock_client):
        login = "testuser"
        repos_data = [{"id": 1, "name": "User Repo"}]
        mock_client._request.return_value = {"data": repos_data}

        result = repo_api.get_user_repos(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/users/{login}/repos", {"offset": 0, "limit": 100}, None
        )
        assert result.data == repos_data

    def test_get_user_repos_with_pagination(self, repo_api, mock_client):
        login = "testuser"
        offset = 5
        limit = 10
        repos_data = [{"id": 2, "name": "User Repo 2"}]
        mock_client._request.return_value = {"data": repos_data}

        result = repo_api.get_user_repos(login, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/users/{login}/repos", {"offset": offset, "limit": limit}, None
        )
        assert result.data == repos_data

    def test_get_group_repos(self, repo_api, mock_client):
        login = "my-group"
        repos_data = [{"id": 1, "name": "Group Repo"}]
        mock_client._request.return_value = {"data": repos_data}

        result = repo_api.get_group_repos(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/repos", {"offset": 0, "limit": 100}, None
        )
        assert result.data == repos_data

    def test_get_group_repos_with_pagination(self, repo_api, mock_client):
        login = "my-group"
        offset = 5
        limit = 10
        repos_data = [{"id": 2, "name": "Group Repo 2"}]
        mock_client._request.return_value = {"data": repos_data}

        result = repo_api.get_group_repos(login, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/repos", {"offset": offset, "limit": limit}, None
        )
        assert result.data == repos_data


class TestRepoAPIToc:
    def test_get_toc(self, repo_api, mock_client):
        book_id = 200
        toc_data = [
            {"title": "Chapter 1", "slug": "chapter-1", "document_id": 1},
            {"title": "Chapter 2", "slug": "chapter-2", "document_id": 2},
        ]
        mock_client._request.return_value = {"data": toc_data}

        result = repo_api.get_toc(book_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{book_id}/toc", None, None
        )
        assert result == toc_data

    def test_get_toc_empty(self, repo_api, mock_client):
        book_id = 200
        mock_client._request.return_value = {}

        result = repo_api.get_toc(book_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{book_id}/toc", None, None
        )
        assert result == []

    def test_get_toc_by_path(self, repo_api, mock_client):
        group_login = "my-group"
        book_slug = "my-book"
        toc_data = [{"title": "Chapter 1", "slug": "chapter-1", "document_id": 1}]
        mock_client._request.return_value = {"data": toc_data}

        result = repo_api.get_toc_by_path(group_login, book_slug)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/repos/{group_login}/{book_slug}/toc", None, None
        )
        assert result == toc_data


class TestRepoAPICreate:
    def test_create_repo(self, repo_api, mock_client, sample_repo_data):
        owner_login = "my-group"
        owner_type = "Group"
        name = "New Repo"
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.create_repo(owner_login, owner_type, name)

        expected_data = {
            "owner_login": owner_login,
            "owner_type": owner_type,
            "name": name,
            "slug": None,
            "description": None,
            "public": 0,
        }
        mock_client._request.assert_called_once_with("POST", "/api/v2/repos", None, expected_data)
        assert result == sample_repo_data

    def test_create_repo_with_all_params(self, repo_api, mock_client, sample_repo_data):
        owner_login = "my-group"
        owner_type = "Group"
        name = "Full Repo"
        slug = "full-repo"
        description = "Full description"
        public = 1
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.create_repo(
            owner_login, owner_type, name, slug=slug, description=description, public=public
        )

        expected_data = {
            "owner_login": owner_login,
            "owner_type": owner_type,
            "name": name,
            "slug": slug,
            "description": description,
            "public": public,
        }
        mock_client._request.assert_called_once_with("POST", "/api/v2/repos", None, expected_data)
        assert result == sample_repo_data

    @pytest.mark.asyncio
    async def test_create_repo_async(self, repo_api, mock_client, sample_repo_data):
        owner_login = "my-group"
        owner_type = "Group"
        name = "New Repo"
        mock_client._request_async.return_value = {"data": sample_repo_data}

        result = await repo_api.create_repo_async(owner_login, owner_type, name)

        expected_data = {
            "owner_login": owner_login,
            "owner_type": owner_type,
            "name": name,
            "slug": None,
            "description": None,
            "public": 0,
        }
        mock_client._request_async.assert_called_once_with(
            "POST", "/api/v2/repos", None, expected_data
        )
        assert result == sample_repo_data


class TestRepoAPIUpdate:
    def test_update_repo(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        name = "Updated Repo"
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.update_repo(book_id, name=name)

        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}", None, {"name": name}
        )
        assert result == sample_repo_data

    def test_update_repo_with_all_params(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        name = "Updated Repo"
        slug = "updated-repo"
        description = "Updated description"
        public = 1
        toc = [{"title": "Chapter 1", "document_id": 1}]
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.update_repo(
            book_id, name=name, slug=slug, description=description, public=public, toc=toc
        )

        expected_data = {
            "name": name,
            "slug": slug,
            "description": description,
            "public": public,
            "toc": toc,
        }
        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}", None, expected_data
        )
        assert result == sample_repo_data

    def test_update_repo_partial(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        description = "New description"
        mock_client._request.return_value = {"data": sample_repo_data}

        result = repo_api.update_repo(book_id, description=description)

        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}", None, {"description": description}
        )
        assert result == sample_repo_data

    @pytest.mark.asyncio
    async def test_update_repo_async(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        name = "Updated Repo"
        mock_client._request_async.return_value = {"data": sample_repo_data}

        result = await repo_api.update_repo_async(book_id, name=name)

        mock_client._request_async.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}", None, {"name": name}
        )
        assert result == sample_repo_data

    @pytest.mark.asyncio
    async def test_update_repo_async_with_all_params(self, repo_api, mock_client, sample_repo_data):
        book_id = 200
        name = "Updated Repo"
        slug = "updated-repo"
        description = "Updated description"
        public = 1
        toc = [{"title": "Chapter 1", "document_id": 1}]
        mock_client._request_async.return_value = {"data": sample_repo_data}

        result = await repo_api.update_repo_async(
            book_id, name=name, slug=slug, description=description, public=public, toc=toc
        )

        expected_data = {
            "name": name,
            "slug": slug,
            "description": description,
            "public": public,
            "toc": toc,
        }
        mock_client._request_async.assert_called_once_with(
            "PUT", f"/api/v2/repos/{book_id}", None, expected_data
        )
        assert result == sample_repo_data


class TestRepoAPIDelete:
    def test_delete_repo(self, repo_api, mock_client):
        book_id = 200
        mock_client._request.return_value = {"data": {"success": True}}

        result = repo_api.delete_repo(book_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{book_id}", None, None
        )
        assert result == {"success": True}

    def test_delete_repo_no_data(self, repo_api, mock_client):
        book_id = 200
        mock_client._request.return_value = {}

        result = repo_api.delete_repo(book_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{book_id}", None, None
        )
        assert result == {}

    @pytest.mark.asyncio
    async def test_delete_repo_async(self, repo_api, mock_client):
        book_id = 200
        mock_client._request_async.return_value = {"data": {"success": True}}

        result = await repo_api.delete_repo_async(book_id)

        mock_client._request_async.assert_called_once_with(
            "DELETE", f"/api/v2/repos/{book_id}", None, None
        )
        assert result == {"success": True}
