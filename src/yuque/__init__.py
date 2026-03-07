"""Yuque Python SDK - A client library for the Yuque OpenAPI.

A modern, type-safe Python client library for the Yuque OpenAPI.

Installation:
    pip install yuque-sdk

Usage:
    from yuque import YuqueClient

    client = YuqueClient(token="your-api-token")
    user = client.user.get_me()
    print(f"Hello, {user.name}!")

For more information, visit: https://github.com/yourusername/yuque-python
"""

from .client import YuqueClient
from .exceptions import (
    AuthenticationError,
    InvalidArgumentError,
    NetworkError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
    YuqueError,
)
from .models import (
    BaseYuqueModel,
    Document,
    DocumentVersion,
    Group,
    GroupMember,
    PaginatedResponse,
    PaginationMeta,
    Repository,
    SearchResult,
    TocNode,
    User,
)

__all__ = [
    # Client
    "YuqueClient",
    # Exceptions
    "YuqueError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "InvalidArgumentError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    # Models
    "BaseYuqueModel",
    "User",
    "Group",
    "GroupMember",
    "Repository",
    "Document",
    "DocumentVersion",
    "TocNode",
    "SearchResult",
    "PaginationMeta",
    "PaginatedResponse",
]

__version__ = "0.1.0"
