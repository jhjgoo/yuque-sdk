"""Tests for UserAPI class."""

from unittest.mock import AsyncMock, Mock

import pytest

from yuque.api.user import UserAPI
from yuque.models import User


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock()
    client._request_async = AsyncMock()
    client._request_paginated = Mock(return_value=[])
    return client


@pytest.fixture
def user_api(mock_client):
    return UserAPI(mock_client)


@pytest.fixture
def sample_user_data():
    return {
        "id": 12345,
        "login": "testuser",
        "name": "Test User",
        "avatar_url": "https://example.com/avatar.png",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "html_url": "https://www.yuque.com/testuser",
    }


class TestUserAPI:
    def test_get_me(self, user_api, mock_client, sample_user_data):
        mock_client._request.return_value = {"data": sample_user_data}

        result = user_api.get_me()

        mock_client._request.assert_called_once_with("GET", "/api/v2/user", None, None)
        assert isinstance(result, User)
        assert result.id == 12345
        assert result.login == "testuser"
        assert result.name == "Test User"

    @pytest.mark.asyncio
    async def test_get_me_async(self, user_api, mock_client, sample_user_data):
        mock_client._request_async.return_value = {"data": sample_user_data}

        result = await user_api.get_me_async()

        mock_client._request_async.assert_called_once_with("GET", "/api/v2/user", None, None)
        assert isinstance(result, User)
        assert result.id == 12345
        assert result.login == "testuser"

    def test_get_by_id(self, user_api, mock_client, sample_user_data):
        user_id = 12345
        mock_client._request.return_value = {"data": sample_user_data}

        result = user_api.get_by_id(user_id)

        mock_client._request.assert_called_once_with("GET", f"/api/v2/users/{user_id}", None, None)
        assert isinstance(result, User)
        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_get_by_id_async(self, user_api, mock_client, sample_user_data):
        user_id = 12345
        mock_client._request_async.return_value = {"data": sample_user_data}

        result = await user_api.get_by_id_async(user_id)

        mock_client._request_async.assert_called_once_with(
            "GET", f"/api/v2/users/{user_id}", None, None
        )
        assert isinstance(result, User)
        assert result.id == user_id

    def test_get_groups(self, user_api, mock_client):
        user_id = 12345
        groups_data = [
            {"id": 1, "login": "group1", "name": "Group 1"},
            {"id": 2, "login": "group2", "name": "Group 2"},
        ]
        mock_client._request_paginated.return_value = groups_data

        result = user_api.get_groups(user_id)

        mock_client._request_paginated.assert_called_once_with(
            "GET", f"/api/v2/users/{user_id}/groups", params={"offset": 0}
        )
        assert result == groups_data

    def test_get_groups_with_offset(self, user_api, mock_client):
        user_id = 12345
        offset = 10
        groups_data = [{"id": 3, "login": "group3", "name": "Group 3"}]
        mock_client._request_paginated.return_value = groups_data

        result = user_api.get_groups(user_id, offset=offset)

        mock_client._request_paginated.assert_called_once_with(
            "GET", f"/api/v2/users/{user_id}/groups", params={"offset": offset}
        )
        assert result == groups_data

    def test_get_me_with_minimal_data(self, user_api, mock_client):
        minimal_user_data = {
            "id": 999,
            "login": "minimal",
            "name": "Minimal User",
        }
        mock_client._request.return_value = {"data": minimal_user_data}

        result = user_api.get_me()

        assert isinstance(result, User)
        assert result.id == 999
        assert result.login == "minimal"
        assert result.name == "Minimal User"
        assert result.avatar_url is None
        assert result.email is None
