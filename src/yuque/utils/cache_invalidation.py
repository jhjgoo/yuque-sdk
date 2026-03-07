"""Cache invalidation utilities.

This module provides helpers for cache invalidation patterns:
- Pattern-based invalidation
- Cascade invalidation
- Invalidation rules

Example:
    ```python
    from yuque.utils.cache_invalidation import invalidate_repo_cache

    # After updating a repo
    invalidate_repo_cache(book_id=123)
    ```
"""

from __future__ import annotations

from ..mcp.cache import get_default_cache


def invalidate_repo_cache(book_id: int | None = None, group_login: str | None = None, book_slug: str | None = None) -> int:
    """Invalidate repository-related cache entries.

    Args:
        book_id: Repository ID.
        group_login: Group login name.
        book_slug: Repository slug.

    Returns:
        Number of cache entries invalidated.
    """
    cache = get_default_cache()
    total_deleted = 0

    # Invalidate by book_id
    if book_id is not None:
        total_deleted += cache.delete_pattern(f"repo:{book_id}")
        total_deleted += cache.delete_pattern(f"toc:{book_id}")
        total_deleted += cache.delete_pattern(f"docs:{book_id}")

    # Invalidate by path
    if group_login and book_slug:
        total_deleted += cache.delete_pattern(f"repo:{group_login}/{book_slug}")
        total_deleted += cache.delete_pattern(f"toc:{group_login}/{book_slug}")
        total_deleted += cache.delete_pattern(f"docs:{group_login}/{book_slug}")

    return total_deleted


async def invalidate_repo_cache_async(
    book_id: int | None = None, group_login: str | None = None, book_slug: str | None = None
) -> int:
    """Async version of invalidate_repo_cache."""
    cache = get_default_cache()
    total_deleted = 0

    # Invalidate by book_id
    if book_id is not None:
        total_deleted += await cache.delete_pattern_async(f"repo:{book_id}")
        total_deleted += await cache.delete_pattern_async(f"toc:{book_id}")
        total_deleted += await cache.delete_pattern_async(f"docs:{book_id}")

    # Invalidate by path
    if group_login and book_slug:
        total_deleted += await cache.delete_pattern_async(f"repo:{group_login}/{book_slug}")
        total_deleted += await cache.delete_pattern_async(f"toc:{group_login}/{book_slug}")
        total_deleted += await cache.delete_pattern_async(f"docs:{group_login}/{book_slug}")

    return total_deleted


def invalidate_doc_cache(doc_id: int | None = None, book_id: int | None = None) -> int:
    """Invalidate document-related cache entries.

    Args:
        doc_id: Document ID.
        book_id: Repository ID.

    Returns:
        Number of cache entries invalidated.
    """
    cache = get_default_cache()
    total_deleted = 0

    # Invalidate by doc_id
    if doc_id is not None:
        total_deleted += cache.delete_pattern(f"doc:{doc_id}")

    # Invalidate by book_id
    if book_id is not None:
        total_deleted += cache.delete_pattern(f"docs:{book_id}")
        total_deleted += cache.delete_pattern(f"toc:{book_id}")

    return total_deleted


async def invalidate_doc_cache_async(doc_id: int | None = None, book_id: int | None = None) -> int:
    """Async version of invalidate_doc_cache."""
    cache = get_default_cache()
    total_deleted = 0

    # Invalidate by doc_id
    if doc_id is not None:
        total_deleted += await cache.delete_pattern_async(f"doc:{doc_id}")

    # Invalidate by book_id
    if book_id is not None:
        total_deleted += await cache.delete_pattern_async(f"docs:{book_id}")
        total_deleted += await cache.delete_pattern_async(f"toc:{book_id}")

    return total_deleted


def invalidate_group_cache(login: str | None = None) -> int:
    """Invalidate group-related cache entries.

    Args:
        login: Group login name.

    Returns:
        Number of cache entries invalidated.
    """
    cache = get_default_cache()
    total_deleted = 0

    if login is not None:
        total_deleted += cache.delete_pattern(f"group:{login}")
        total_deleted += cache.delete_pattern(f"repos:{login}")
        total_deleted += cache.delete_pattern(f"members:{login}")

    return total_deleted


async def invalidate_group_cache_async(login: str | None = None) -> int:
    """Async version of invalidate_group_cache."""
    cache = get_default_cache()
    total_deleted = 0

    if login is not None:
        total_deleted += await cache.delete_pattern_async(f"group:{login}")
        total_deleted += await cache.delete_pattern_async(f"repos:{login}")
        total_deleted += await cache.delete_pattern_async(f"members:{login}")

    return total_deleted


__all__ = [
    "invalidate_repo_cache",
    "invalidate_repo_cache_async",
    "invalidate_doc_cache",
    "invalidate_doc_cache_async",
    "invalidate_group_cache",
    "invalidate_group_cache_async",
]
