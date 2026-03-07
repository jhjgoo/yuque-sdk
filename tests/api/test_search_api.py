"""Tests for SearchAPI class."""

from unittest.mock import Mock

import pytest

from yuque.api.search import SearchAPI
from yuque.models import PaginatedResponse


@pytest.fixture
def mock_client():
    client = Mock()
    client._request = Mock(return_value={"data": []})
    return client


@pytest.fixture
def search_api(mock_client):
    return SearchAPI(mock_client)


class TestSearchAPI:
    def test_search_default_params(self, search_api, mock_client):
        keyword = "python"
        search_results = [
            {"id": 1, "type": "doc", "title": "Python Guide", "url": "https://example.com/doc1"},
            {"id": 2, "type": "doc", "title": "Python Tutorial", "url": "https://example.com/doc2"},
        ]
        mock_client._request.return_value = {
            "data": search_results,
            "meta": {"page": 1, "per_page": 20, "total": 2, "total_pages": 1},
        }

        result = search_api.search(keyword)

        expected_params = {"q": keyword, "type": "doc", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert isinstance(result, PaginatedResponse)
        assert result.data == search_results

    def test_search_with_custom_type(self, search_api, mock_client):
        keyword = "api"
        search_type = "book"
        search_results = [
            {"id": 1, "type": "book", "title": "API Design", "url": "https://example.com/book1"},
        ]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, type=search_type)

        expected_params = {"q": keyword, "type": search_type, "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_with_custom_page(self, search_api, mock_client):
        keyword = "test"
        page = 3
        search_results = [{"id": 5, "type": "doc", "title": "Test Doc"}]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, page=page)

        expected_params = {"q": keyword, "type": "doc", "page": page}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_type_doc(self, search_api, mock_client):
        keyword = "documentation"
        search_results = [
            {"id": 1, "type": "doc", "title": "Documentation Guide"},
        ]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, type="doc")

        expected_params = {"q": keyword, "type": "doc", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_type_book(self, search_api, mock_client):
        keyword = "knowledge"
        search_results = [
            {"id": 1, "type": "book", "title": "Knowledge Base"},
        ]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, type="book")

        expected_params = {"q": keyword, "type": "book", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_type_user(self, search_api, mock_client):
        keyword = "john"
        search_results = [
            {"id": 1, "type": "user", "title": "John Doe", "login": "johndoe"},
        ]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, type="user")

        expected_params = {"q": keyword, "type": "user", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_type_group(self, search_api, mock_client):
        keyword = "engineering"
        search_results = [
            {"id": 1, "type": "group", "title": "Engineering Team", "login": "eng"},
        ]
        mock_client._request.return_value = {"data": search_results}

        result = search_api.search(keyword, type="group")

        expected_params = {"q": keyword, "type": "group", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == search_results

    def test_search_empty_results(self, search_api, mock_client):
        keyword = "nonexistent"
        mock_client._request.return_value = {"data": []}

        result = search_api.search(keyword)

        expected_params = {"q": keyword, "type": "doc", "page": 1}
        mock_client._request.assert_called_once_with("GET", "/api/v2/search", expected_params, None)
        assert result.data == []

    def test_search_with_pagination_meta(self, search_api, mock_client):
        keyword = "guide"
        search_results = [{"id": 1, "type": "doc", "title": "Guide"}]
        mock_client._request.return_value = {
            "data": search_results,
            "meta": {"page": 1, "per_page": 20, "total": 100, "total_pages": 5},
        }

        result = search_api.search(keyword)

        assert isinstance(result, PaginatedResponse)
        assert result.data == search_results
        assert result.meta is not None
        assert result.meta.page == 1
        assert result.meta.per_page == 20
        assert result.meta.total == 100
        assert result.meta.total_pages == 5
