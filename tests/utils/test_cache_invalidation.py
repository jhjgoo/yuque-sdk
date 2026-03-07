"""Tests for cache invalidation utilities."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yuque.utils.cache_invalidation import (
    invalidate_doc_cache,
    invalidate_doc_cache_async,
    invalidate_group_cache,
    invalidate_group_cache_async,
    invalidate_repo_cache,
    invalidate_repo_cache_async,
)


class TestInvalidateRepoCache:
    """Tests for invalidate_repo_cache (sync version)."""

    def test_with_book_id_only(self) -> None:
        """Invalidate cache by book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [3, 2, 5]  # repo, toc, docs

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(book_id=123)

        assert result == 10
        mock_cache.delete_pattern.assert_any_call("repo:123")
        mock_cache.delete_pattern.assert_any_call("toc:123")
        mock_cache.delete_pattern.assert_any_call("docs:123")

    def test_with_path_only(self) -> None:
        """Invalidate cache by group_login and book_slug."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [2, 1, 3]  # repo, toc, docs

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(group_login="my-group", book_slug="my-repo")

        assert result == 6
        mock_cache.delete_pattern.assert_any_call("repo:my-group/my-repo")
        mock_cache.delete_pattern.assert_any_call("toc:my-group/my-repo")
        mock_cache.delete_pattern.assert_any_call("docs:my-group/my-repo")

    def test_with_both_book_id_and_path(self) -> None:
        """Invalidate cache by both book_id and path."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [3, 2, 5, 2, 1, 3]

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(book_id=123, group_login="my-group", book_slug="my-repo")

        assert result == 16

    def test_with_no_parameters(self) -> None:
        """Return 0 when no parameters provided."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache()

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()

    def test_with_none_parameters(self) -> None:
        """Handle None parameters gracefully."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(book_id=None, group_login=None, book_slug=None)

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()

    def test_with_missing_book_slug(self) -> None:
        """Path invalidation skipped if book_slug missing."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [3, 2, 5]

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(book_id=123, group_login="my-group")

        assert result == 10
        assert mock_cache.delete_pattern.call_count == 3

    def test_with_missing_group_login(self) -> None:
        """Path invalidation skipped if group_login missing."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [3, 2, 5]

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_repo_cache(book_id=123, book_slug="my-repo")

        assert result == 10
        assert mock_cache.delete_pattern.call_count == 3


class TestInvalidateRepoCacheAsync:
    """Tests for invalidate_repo_cache_async (async version)."""

    @pytest.mark.asyncio
    async def test_with_book_id_only(self) -> None:
        """Async invalidate cache by book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[3, 2, 5])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_repo_cache_async(book_id=123)

        assert result == 10
        mock_cache.delete_pattern_async.assert_any_call("repo:123")
        mock_cache.delete_pattern_async.assert_any_call("toc:123")
        mock_cache.delete_pattern_async.assert_any_call("docs:123")

    @pytest.mark.asyncio
    async def test_with_path_only(self) -> None:
        """Async invalidate cache by path."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[2, 1, 3])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_repo_cache_async(group_login="my-group", book_slug="my-repo")

        assert result == 6
        mock_cache.delete_pattern_async.assert_any_call("repo:my-group/my-repo")

    @pytest.mark.asyncio
    async def test_with_both_parameters(self) -> None:
        """Async invalidate with both book_id and path."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[3, 2, 5, 2, 1, 3])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_repo_cache_async(
                book_id=123, group_login="my-group", book_slug="my-repo"
            )

        assert result == 16

    @pytest.mark.asyncio
    async def test_with_no_parameters(self) -> None:
        """Async return 0 when no parameters."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_repo_cache_async()

        assert result == 0
        mock_cache.delete_pattern_async.assert_not_called()


class TestInvalidateDocCache:
    """Tests for invalidate_doc_cache (sync version)."""

    def test_with_doc_id_only(self) -> None:
        """Invalidate cache by doc_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.return_value = 5

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_doc_cache(doc_id=456)

        assert result == 5
        mock_cache.delete_pattern.assert_called_once_with("doc:456")

    def test_with_book_id_only(self) -> None:
        """Invalidate cache by book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [3, 2]  # docs, toc

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_doc_cache(book_id=123)

        assert result == 5
        mock_cache.delete_pattern.assert_any_call("docs:123")
        mock_cache.delete_pattern.assert_any_call("toc:123")

    def test_with_both_doc_id_and_book_id(self) -> None:
        """Invalidate cache by both doc_id and book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [5, 3, 2]  # doc, docs, toc

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_doc_cache(doc_id=456, book_id=123)

        assert result == 10
        mock_cache.delete_pattern.assert_any_call("doc:456")
        mock_cache.delete_pattern.assert_any_call("docs:123")
        mock_cache.delete_pattern.assert_any_call("toc:123")

    def test_with_no_parameters(self) -> None:
        """Return 0 when no parameters provided."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_doc_cache()

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()

    def test_with_none_parameters(self) -> None:
        """Handle None parameters gracefully."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_doc_cache(doc_id=None, book_id=None)

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()


class TestInvalidateDocCacheAsync:
    """Tests for invalidate_doc_cache_async (async version)."""

    @pytest.mark.asyncio
    async def test_with_doc_id_only(self) -> None:
        """Async invalidate cache by doc_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(return_value=5)

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_doc_cache_async(doc_id=456)

        assert result == 5
        mock_cache.delete_pattern_async.assert_called_once_with("doc:456")

    @pytest.mark.asyncio
    async def test_with_book_id_only(self) -> None:
        """Async invalidate cache by book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[3, 2])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_doc_cache_async(book_id=123)

        assert result == 5

    @pytest.mark.asyncio
    async def test_with_both_parameters(self) -> None:
        """Async invalidate with both doc_id and book_id."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[5, 3, 2])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_doc_cache_async(doc_id=456, book_id=123)

        assert result == 10

    @pytest.mark.asyncio
    async def test_with_no_parameters(self) -> None:
        """Async return 0 when no parameters."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_doc_cache_async()

        assert result == 0
        mock_cache.delete_pattern_async.assert_not_called()


class TestInvalidateGroupCache:
    """Tests for invalidate_group_cache (sync version)."""

    def test_with_login(self) -> None:
        """Invalidate cache by group login."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.side_effect = [2, 5, 3]  # group, repos, members

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_group_cache(login="my-group")

        assert result == 10
        mock_cache.delete_pattern.assert_any_call("group:my-group")
        mock_cache.delete_pattern.assert_any_call("repos:my-group")
        mock_cache.delete_pattern.assert_any_call("members:my-group")

    def test_with_no_login(self) -> None:
        """Return 0 when login not provided."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_group_cache()

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()

    def test_with_none_login(self) -> None:
        """Handle None login gracefully."""
        mock_cache = MagicMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = invalidate_group_cache(login=None)

        assert result == 0
        mock_cache.delete_pattern.assert_not_called()

    def test_pattern_string_format(self) -> None:
        """Verify correct pattern format for group."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.return_value = 1

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            invalidate_group_cache(login="test-group")

        calls = [call.args[0] for call in mock_cache.delete_pattern.call_args_list]
        assert "group:test-group" in calls
        assert "repos:test-group" in calls
        assert "members:test-group" in calls


class TestInvalidateGroupCacheAsync:
    """Tests for invalidate_group_cache_async (async version)."""

    @pytest.mark.asyncio
    async def test_with_login(self) -> None:
        """Async invalidate cache by group login."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock(side_effect=[2, 5, 3])

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_group_cache_async(login="my-group")

        assert result == 10
        mock_cache.delete_pattern_async.assert_any_call("group:my-group")
        mock_cache.delete_pattern_async.assert_any_call("repos:my-group")
        mock_cache.delete_pattern_async.assert_any_call("members:my-group")

    @pytest.mark.asyncio
    async def test_with_no_login(self) -> None:
        """Async return 0 when login not provided."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_group_cache_async()

        assert result == 0
        mock_cache.delete_pattern_async.assert_not_called()

    @pytest.mark.asyncio
    async def test_with_none_login(self) -> None:
        """Async handle None login gracefully."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern_async = AsyncMock()

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            result = await invalidate_group_cache_async(login=None)

        assert result == 0
        mock_cache.delete_pattern_async.assert_not_called()


class TestPatternFormats:
    """Tests for cache key pattern formats."""

    def test_repo_pattern_format(self) -> None:
        """Repo patterns follow correct format."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.return_value = 1

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            invalidate_repo_cache(book_id=999)

        patterns = [call.args[0] for call in mock_cache.delete_pattern.call_args_list]
        assert all(
            p.startswith("repo:") or p.startswith("toc:") or p.startswith("docs:") for p in patterns
        )
        assert all(":999" in p for p in patterns)

    def test_doc_pattern_format(self) -> None:
        """Doc patterns follow correct format."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.return_value = 1

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            invalidate_doc_cache(doc_id=777)

        patterns = [call.args[0] for call in mock_cache.delete_pattern.call_args_list]
        assert all(p.startswith("doc:") for p in patterns)

    def test_path_pattern_with_slash(self) -> None:
        """Path patterns contain slash separator."""
        mock_cache = MagicMock()
        mock_cache.delete_pattern.return_value = 1

        with patch("yuque.utils.cache_invalidation.get_default_cache", return_value=mock_cache):
            invalidate_repo_cache(group_login="team", book_slug="docs")

        patterns = [call.args[0] for call in mock_cache.delete_pattern.call_args_list]
        assert all("team/docs" in p for p in patterns)
