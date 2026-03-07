"""Tests for GroupAPI class."""

from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from yuque.api.group import GroupAPI
from yuque.models import PaginatedResponse


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock(return_value={"data": {}})
    client._request_async = AsyncMock(return_value={"data": {}})
    return client


@pytest.fixture
def group_api(mock_client):
    return GroupAPI(mock_client)


@pytest.fixture
def sample_group_data():
    return {
        "id": 100,
        "login": "my-group",
        "name": "My Group",
        "description": "Test group",
        "owner_id": 1,
        "members_count": 10,
        "books_count": 5,
    }


class TestGroupAPIGet:
    def test_get(self, group_api, mock_client, sample_group_data):
        login = "my-group"
        mock_client._request.return_value = {"data": sample_group_data}

        result = group_api.get(login)

        mock_client._request.assert_called_once_with("GET", f"/api/v2/groups/{login}", None, None)
        assert result == sample_group_data

    def test_get_by_id(self, group_api, mock_client, sample_group_data):
        group_id = 100
        mock_client._request.return_value = {"data": sample_group_data}

        result = group_api.get_by_id(group_id)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{group_id}", None, None
        )
        assert result == sample_group_data

    @pytest.mark.asyncio
    async def test_get_by_id_async(self, group_api, mock_client, sample_group_data):
        group_id = 100
        mock_client._request_async.return_value = {"data": sample_group_data}

        result = await group_api.get_by_id_async(group_id)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{group_id}", None, None
        )
        assert result == sample_group_data

    def test_get_repos(self, group_api, mock_client):
        login = "my-group"
        repos_data = [{"id": 1, "name": "Repo 1"}, {"id": 2, "name": "Repo 2"}]
        mock_client._request.return_value = {"data": repos_data}

        result = group_api.get_repos(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/repos", {"offset": 0, "limit": 100}, None
        )
        assert isinstance(result, PaginatedResponse)
        assert result.data == repos_data

    def test_get_repos_with_pagination(self, group_api, mock_client):
        login = "my-group"
        offset = 10
        limit = 20
        repos_data = [{"id": 3, "name": "Repo 3"}]
        mock_client._request.return_value = {"data": repos_data}

        result = group_api.get_repos(login, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/repos", {"offset": offset, "limit": limit}, None
        )
        assert result.data == repos_data


class TestGroupAPIMembers:
    def test_get_members(self, group_api, mock_client):
        login = "my-group"
        members_data = [{"id": 1, "name": "Member 1"}, {"id": 2, "name": "Member 2"}]
        mock_client._request.return_value = {"data": members_data}

        result = group_api.get_members(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/users", {"offset": 0, "limit": 100}, None
        )
        assert isinstance(result, PaginatedResponse)
        assert result.data == members_data

    def test_get_members_with_pagination(self, group_api, mock_client):
        login = "my-group"
        offset = 10
        limit = 20
        members_data = [{"id": 3, "name": "Member 3"}]
        mock_client._request.return_value = {"data": members_data}

        result = group_api.get_members(login, offset=offset, limit=limit)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/users", {"offset": offset, "limit": limit}, None
        )
        assert result.data == members_data

    def test_add_member(self, group_api, mock_client):
        login = "my-group"
        user_id = 123
        role = 1
        mock_client._request.return_value = {"data": {"success": True}}

        result = group_api.add_member(login, user_id, role)

        mock_client._request.assert_called_once_with(
            "POST", f"/api/v2/groups/{login}/users", None, {"user_id": user_id, "role": role}
        )
        assert result == {"success": True}

    def test_add_member_default_role(self, group_api, mock_client):
        login = "my-group"
        user_id = 123
        mock_client._request.return_value = {"data": {}}

        result = group_api.add_member(login, user_id)

        mock_client._request.assert_called_once_with(
            "POST", f"/api/v2/groups/{login}/users", None, {"user_id": user_id, "role": 1}
        )
        assert result == {}

    def test_update_member(self, group_api, mock_client):
        login = "my-group"
        user_id = 123
        role = 0
        mock_client._request.return_value = {"data": {"success": True}}

        result = group_api.update_member(login, user_id, role)

        mock_client._request.assert_called_once_with(
            "PUT", f"/api/v2/groups/{login}/users/{user_id}", None, {"role": role}
        )
        assert result == {"success": True}

    def test_remove_member(self, group_api, mock_client):
        login = "my-group"
        user_id = 123
        mock_client._request.return_value = {"data": {"success": True}}

        result = group_api.remove_member(login, user_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/groups/{login}/users/{user_id}", None, None
        )
        assert result == {"success": True}

    def test_remove_member_no_data(self, group_api, mock_client):
        login = "my-group"
        user_id = 123
        mock_client._request.return_value = {}

        result = group_api.remove_member(login, user_id)

        mock_client._request.assert_called_once_with(
            "DELETE", f"/api/v2/groups/{login}/users/{user_id}", None, None
        )
        assert result == {}


class TestGroupAPIStatistics:
    def test_get_statistics(self, group_api, mock_client):
        login = "my-group"
        stats_data = {"members_count": 10, "books_count": 5, "docs_count": 100}
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_statistics(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/statistics", None, None
        )
        assert result == stats_data

    def test_get_member_stats(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"user_id": 1, "docs_count": 10}, {"user_id": 2, "docs_count": 20}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_member_stats(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/members", {"page": 1, "limit": 20}, None
        )
        assert isinstance(result, PaginatedResponse)
        assert result.data == stats_data

    def test_get_member_stats_with_filters(self, group_api, mock_client):
        login = "my-group"
        name = "John"
        range_period = "30d"
        page = 2
        limit = 10
        sortField = "created_at"
        sortOrder = "desc"
        stats_data = [{"user_id": 1, "name": "John", "docs_count": 5}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_member_stats(
            login,
            name=name,
            range=range_period,
            page=page,
            limit=limit,
            sortField=sortField,
            sortOrder=sortOrder,
        )

        expected_params = {
            "page": page,
            "limit": limit,
            "name": name,
            "range": range_period,
            "sortField": sortField,
            "sortOrder": sortOrder,
        }
        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/members", expected_params, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_member_stats_async(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"user_id": 1, "docs_count": 10}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_member_stats_async(login)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/members", {"page": 1, "limit": 20}, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_member_stats_async_with_all_params(self, group_api, mock_client):
        login = "my-group"
        name = "John"
        range_period = "30d"
        page = 2
        limit = 10
        sortField = "docs_count"
        sortOrder = "desc"
        stats_data = [{"user_id": 1, "name": "John", "docs_count": 50}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_member_stats_async(
            login,
            name=name,
            range=range_period,
            page=page,
            limit=limit,
            sortField=sortField,
            sortOrder=sortOrder,
        )

        expected_params = {
            "page": page,
            "limit": limit,
            "name": name,
            "range": range_period,
            "sortField": sortField,
            "sortOrder": sortOrder,
        }
        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/members", expected_params, None
        )
        assert result.data == stats_data

    def test_get_book_stats(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"book_id": 1, "name": "Book 1", "docs_count": 50}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_book_stats(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/books", {"page": 1, "limit": 20}, None
        )
        assert result.data == stats_data

    def test_get_book_stats_with_filters(self, group_api, mock_client):
        login = "my-group"
        name = "API"
        range_period = "7d"
        page = 2
        limit = 10
        stats_data = [{"book_id": 1, "name": "API Docs", "docs_count": 30}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_book_stats(
            login, name=name, range=range_period, page=page, limit=limit
        )

        expected_params = {"page": page, "limit": limit, "name": name, "range": range_period}
        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/books", expected_params, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_book_stats_async(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"book_id": 1, "name": "Book 1", "docs_count": 50}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_book_stats_async(login)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/books", {"page": 1, "limit": 20}, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_book_stats_async_with_filters(self, group_api, mock_client):
        login = "my-group"
        name = "API"
        range_period = "7d"
        page = 2
        limit = 10
        stats_data = [{"book_id": 1, "name": "API Guide", "docs_count": 30}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_book_stats_async(
            login, name=name, range=range_period, page=page, limit=limit
        )

        expected_params = {"page": page, "limit": limit, "name": name, "range": range_period}
        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/books", expected_params, None
        )
        assert result.data == stats_data

    def test_get_doc_stats(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"doc_id": 1, "title": "Doc 1", "read_count": 100}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_doc_stats(login)

        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/docs", {"page": 1, "limit": 20}, None
        )
        assert result.data == stats_data

    def test_get_doc_stats_with_filters(self, group_api, mock_client):
        login = "my-group"
        title = "Introduction"
        range_period = "90d"
        page = 2
        limit = 10
        stats_data = [{"doc_id": 1, "title": "Introduction", "read_count": 500}]
        mock_client._request.return_value = {"data": stats_data}

        result = group_api.get_doc_stats(
            login, title=title, range=range_period, page=page, limit=limit
        )

        expected_params = {"page": page, "limit": limit, "title": title, "range": range_period}
        mock_client._request.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/docs", expected_params, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_doc_stats_async(self, group_api, mock_client):
        login = "my-group"
        stats_data = [{"doc_id": 1, "title": "Doc 1", "read_count": 100}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_doc_stats_async(login)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/docs", {"page": 1, "limit": 20}, None
        )
        assert result.data == stats_data

    @pytest.mark.asyncio
    async def test_get_doc_stats_async_with_filters(self, group_api, mock_client):
        login = "my-group"
        title = "Getting Started"
        range_period = "90d"
        page = 2
        limit = 10
        stats_data = [{"doc_id": 1, "title": "Getting Started Guide", "read_count": 500}]
        mock_client._request_async.return_value = {"data": stats_data}

        result = await group_api.get_doc_stats_async(
            login, title=title, range=range_period, page=page, limit=limit
        )

        expected_params = {"page": page, "limit": limit, "title": title, "range": range_period}
        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/groups/{login}/stats/docs", expected_params, None
        )
        assert result.data == stats_data
