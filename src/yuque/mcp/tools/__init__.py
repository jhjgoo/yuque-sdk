"""MCP tools for Yuque API.

This module provides MCP tool implementations for various Yuque API endpoints.
Each tool is implemented as a standalone module.

Available tool modules:
- user: User-related tools (get current user, get user by ID, get user groups)
- repo: Repository tools (get repos, list repos, get TOC)
- group: Group tools (get group, members, statistics)
- doc: Document tools (get, create, update, delete documents)
- search: Search tools (search across Yuque content)
"""

from __future__ import annotations

from .doc import register_doc_tools
from .group import register_group_tools
from .repo import register_repo_tools
from .search import register_search_tools
from .user import register_user_tools

__all__ = [
    "register_doc_tools",
    "register_group_tools",
    "register_repo_tools",
    "register_search_tools",
    "register_user_tools",
]
