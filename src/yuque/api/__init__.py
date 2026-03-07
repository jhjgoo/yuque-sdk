"""Yuque API endpoints."""

from .base import BaseAPI
from .doc import DocAPI
from .group import GroupAPI
from .repo import RepoAPI
from .search import SearchAPI
from .user import UserAPI

__all__ = [
    "BaseAPI",
    "UserAPI",
    "GroupAPI",
    "RepoAPI",
    "DocAPI",
    "SearchAPI",
]
