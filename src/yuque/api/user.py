"""User API endpoints."""

from __future__ import annotations

from typing import Any

from ..models import User
from .base import BaseAPI


class UserAPI(BaseAPI):
    """API endpoints for user operations."""

    def get_me(self) -> User:
        """Get the current authenticated user."""
        response = self._request("GET", "/api/v2/user")
        return User(**response["data"])

    async def get_me_async(self) -> User:
        """Async version of get_me()."""
        response = await self._request_async("GET", "/api/v2/user")
        return User(**response["data"])

    def get_by_id(self, user_id: int) -> User:
        """Get a user by their ID."""
        response = self._request("GET", f"/api/v2/users/{user_id}")
        return User(**response["data"])

    async def get_by_id_async(self, user_id: int) -> User:
        """Async version of get_by_id()."""
        response = await self._request_async("GET", f"/api/v2/users/{user_id}")
        return User(**response["data"])

    def get_groups(self, user_id: int, offset: int = 0) -> list[dict[str, Any]]:
        """Get groups that a user belongs to."""
        return self._client._request_paginated(
            "GET", f"/api/v2/users/{user_id}/groups", params={"offset": offset}
        )
