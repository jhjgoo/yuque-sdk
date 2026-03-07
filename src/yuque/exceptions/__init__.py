"""Yuque API client exceptions."""

from __future__ import annotations

from typing import Any


class YuqueError(Exception):
    """Base exception for Yuque API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(YuqueError):
    """Raised when authentication fails (401 status code)."""

    def __init__(
        self,
        message: str = "Authentication failed. Please check your API token.",
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=401, response_data=response_data)


class PermissionDeniedError(YuqueError):
    """Raised when user lacks required permissions (403 status code)."""

    def __init__(
        self,
        message: str = "You don't have permission to perform this action.",
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=403, response_data=response_data)


class NotFoundError(YuqueError):
    """Raised when a resource is not found (404 status code)."""

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=404, response_data=response_data)


class InvalidArgumentError(YuqueError):
    """Raised when request arguments are invalid (400 status code)."""

    def __init__(
        self,
        message: str = "Invalid request arguments.",
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=400, response_data=response_data)


class ValidationError(YuqueError):
    """Raised when request validation fails (422 status code)."""

    def __init__(
        self,
        message: str = "Request validation failed.",
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=422, response_data=response_data)


class RateLimitError(YuqueError):
    """Raised when API rate limit is exceeded (429 status code)."""

    def __init__(
        self,
        message: str = "API rate limit exceeded. Please try again later.",
        retry_after: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=429, response_data=response_data)
        self.retry_after = retry_after


class ServerError(YuqueError):
    """Raised when server returns an error (500+ status codes)."""

    def __init__(
        self,
        message: str = "Server error occurred.",
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_data=response_data)


class NetworkError(YuqueError):
    """Raised when a network error occurs."""

    def __init__(self, message: str = "Network error occurred.") -> None:
        super().__init__(message)


class AsyncClientNotAvailableError(YuqueError):
    """Raised when async client is not available but async operation is requested."""

    def __init__(
        self,
        message: str = "Async client is not available. Please use async_client() method.",
    ) -> None:
        super().__init__(message)
