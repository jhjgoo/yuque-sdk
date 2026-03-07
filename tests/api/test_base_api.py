"""Tests for BaseAPI class."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock

import httpx
import pytest

from yuque.api.base import BaseAPI
from yuque.exceptions import (
    AuthenticationError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
    YuqueError,
)
from yuque.models import PaginatedResponse


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock(return_value={"data": {}})
    client._request_async = AsyncMock(return_value={"data": {}})
    return client


@pytest.fixture
def base_api(mock_client):
    return BaseAPI(mock_client)


class TestBaseAPIInit:
    def test_init_with_client(self, mock_client):
        api = BaseAPI(mock_client)
        assert api._client is mock_client


class TestHandleResponse:
    def test_handle_response_success_with_json(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.is_success = True
        response.json = Mock(return_value={"data": {"id": 1, "name": "test"}})

        result = base_api._handle_response(response)

        assert result == {"data": {"id": 1, "name": "test"}}

    def test_handle_response_success_empty(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.is_success = True
        response.json = Mock(side_effect=Exception("No JSON"))

        result = base_api._handle_response(response)

        assert result == {}

    def test_handle_response_400_invalid_argument(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 400
        response.is_success = False
        response.json = Mock(return_value={"error": "Invalid argument"})
        response.text = "Invalid argument"

        with pytest.raises(InvalidArgumentError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 400
        assert exc_info.value.response_data == {"error": "Invalid argument"}

    def test_handle_response_401_authentication(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 401
        response.is_success = False
        response.json = Mock(return_value={"error": "Unauthorized"})
        response.text = "Unauthorized"

        with pytest.raises(AuthenticationError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 401

    def test_handle_response_403_permission_denied(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 403
        response.is_success = False
        response.json = Mock(return_value={"error": "Forbidden"})
        response.text = "Forbidden"

        with pytest.raises(PermissionDeniedError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 403

    def test_handle_response_404_not_found(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 404
        response.is_success = False
        response.json = Mock(return_value={"error": "Not found"})
        response.text = "Not found"

        with pytest.raises(NotFoundError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 404

    def test_handle_response_422_validation(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 422
        response.is_success = False
        response.json = Mock(return_value={"error": "Validation failed"})
        response.text = "Validation failed"

        with pytest.raises(ValidationError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 422

    def test_handle_response_429_rate_limit(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 429
        response.is_success = False
        response.json = Mock(return_value={"error": "Rate limit exceeded"})
        response.text = "Rate limit exceeded"
        response.headers = {"Retry-After": "60"}

        with pytest.raises(RateLimitError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_handle_response_429_rate_limit_no_retry_after(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 429
        response.is_success = False
        response.json = Mock(return_value={"error": "Rate limit exceeded"})
        response.text = "Rate limit exceeded"
        response.headers = {}

        with pytest.raises(RateLimitError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after is None

    def test_handle_response_500_server_error(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 500
        response.is_success = False
        response.json = Mock(return_value={"error": "Internal server error"})
        response.text = "Internal server error"

        with pytest.raises(ServerError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 500

    def test_handle_response_502_bad_gateway(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 502
        response.is_success = False
        response.json = Mock(return_value={"error": "Bad gateway"})
        response.text = "Bad gateway"

        with pytest.raises(ServerError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 502

    def test_handle_response_other_error(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 418
        response.is_success = False
        response.json = Mock(return_value={})
        response.text = "I'm a teapot"

        with pytest.raises(YuqueError) as exc_info:
            base_api._handle_response(response)

        assert exc_info.value.status_code == 418

    def test_handle_response_no_error_message(self, base_api):
        response = Mock(spec=httpx.Response)
        response.status_code = 400
        response.is_success = False
        response.json = Mock(return_value={})
        response.text = ""

        with pytest.raises(InvalidArgumentError) as exc_info:
            base_api._handle_response(response)

        assert "HTTP 400 error" in str(exc_info.value)


class TestRequest:
    def test_request_get(self, base_api, mock_client):
        mock_client._request.return_value = {"data": {"id": 1}}

        result = base_api._request("GET", "/api/v2/test")

        mock_client._request.assert_called_once_with("GET", "/api/v2/test", None, None)
        assert result == {"data": {"id": 1}}

    def test_request_post_with_data(self, base_api, mock_client):
        mock_client._request.return_value = {"data": {"id": 2}}
        json_data = {"name": "test"}

        result = base_api._request("POST", "/api/v2/test", json_data=json_data)

        mock_client._request.assert_called_once_with("POST", "/api/v2/test", None, json_data)
        assert result == {"data": {"id": 2}}

    def test_request_with_params(self, base_api, mock_client):
        mock_client._request.return_value = {"data": []}
        params = {"page": 1, "limit": 20}

        result = base_api._request("GET", "/api/v2/test", params=params)

        mock_client._request.assert_called_once_with("GET", "/api/v2/test", params, None)
        assert result == {"data": []}


class TestRequestAsync:
    @pytest.mark.asyncio
    async def test_request_async_get(self, base_api, mock_client):
        mock_client._request_async.return_value = {"data": {"id": 1}}

        result = await base_api._request_async("GET", "/api/v2/test")

        mock_client._request_async.assert_called_once_with("GET", "/api/v2/test", None, None)
        assert result == {"data": {"id": 1}}

    @pytest.mark.asyncio
    async def test_request_async_post_with_data(self, base_api, mock_client):
        mock_client._request_async.return_value = {"data": {"id": 2}}
        json_data = {"name": "test"}

        result = await base_api._request_async("POST", "/api/v2/test", json_data=json_data)

        mock_client._request_async.assert_called_once_with("POST", "/api/v2/test", None, json_data)
        assert result == {"data": {"id": 2}}


class TestParsePaginatedResponse:
    def test_parse_paginated_response_with_data(self, base_api):
        response = {
            "data": [{"id": 1}, {"id": 2}],
            "meta": {"page": 1, "per_page": 20, "total": 2, "total_pages": 1},
        }

        result = base_api._parse_paginated_response(response)

        assert isinstance(result, PaginatedResponse)
        assert result.data == [{"id": 1}, {"id": 2}]
        assert result.meta is not None
        assert result.meta.page == 1
        assert result.meta.per_page == 20
        assert result.meta.total == 2

    def test_parse_paginated_response_without_meta(self, base_api):
        response = {"data": [{"id": 1}, {"id": 2}]}

        result = base_api._parse_paginated_response(response)

        assert isinstance(result, PaginatedResponse)
        assert result.data == [{"id": 1}, {"id": 2}]
        assert result.meta is None

    def test_parse_paginated_response_empty_data(self, base_api):
        response = {}

        result = base_api._parse_paginated_response(response)

        assert isinstance(result, PaginatedResponse)
        assert result.data == []

    def test_parse_paginated_response_single_item(self, base_api):
        response = {"data": {"id": 1}}

        result = base_api._parse_paginated_response(response)

        assert isinstance(result, PaginatedResponse)
        assert result.data == [{"id": 1}]

    def test_parse_paginated_response_custom_data_key(self, base_api):
        response = {
            "items": [{"id": 1}, {"id": 2}],
            "meta": {"page": 1, "per_page": 20, "total": 2, "total_pages": 1},
        }

        result = base_api._parse_paginated_response(response, data_key="items")

        assert isinstance(result, PaginatedResponse)
        assert result.data == [{"id": 1}, {"id": 2}]
