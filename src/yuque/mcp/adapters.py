"""Error adapters for MCP protocol.

This module provides error handling and adaptation between
Yuque API exceptions and MCP protocol error responses.

Maps Yuque-specific exceptions to appropriate MCP error codes
and messages for consistent error handling across the protocol.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from yuque.exceptions import (
    AsyncClientNotAvailableError,
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

if TYPE_CHECKING:
    pass


class MCPError:
    """MCP protocol error representation.

    Encapsulates error information in a format compatible with
    MCP protocol error responses.

    Args:
        code: Error code (negative for protocol errors, positive for tool errors).
        message: Human-readable error message.
        data: Optional additional error data.

    Example:
        ```python
        error = MCPError(
            code=-32001,
            message="Authentication failed",
            data={"hint": "Check your API token"}
        )
        ```
    """

    def __init__(
        self,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize MCP error."""
        self.code = code
        self.message = message
        self.data = data or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert error to MCP error response format.

        Returns:
            Dictionary with error code, message, and optional data.
        """
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.data:
            result["data"] = self.data
        return result

    def to_tool_error(self) -> dict[str, Any]:
        """Convert error to MCP tool execution error format.

        Returns:
            Dictionary with isError flag and error content.
        """
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": self.message,
                }
            ],
            "error": self.to_dict(),
        }


class ErrorAdapter:
    """Adapter for converting Yuque exceptions to MCP errors.

    This class provides methods to transform Yuque API exceptions
    into MCP-friendly error responses with helpful messages and
    self-correction suggestions.

    Example:
        ```python
        adapter = ErrorAdapter()
        try:
            # Yuque API call
            pass
        except AuthenticationError as e:
            mcp_error = adapter.adapt_exception(e)
            return mcp_error.to_tool_error()
        ```
    """

    ERROR_CODES: dict[type[Exception], int] = {
        # Using -32xxx range for Yuque-specific errors (per JSON-RPC spec)
        AuthenticationError: -32001,
        PermissionDeniedError: -32002,
        NotFoundError: -32003,
        InvalidArgumentError: -32004,
        ValidationError: -32005,
        RateLimitError: -32006,
        ServerError: -32007,
        NetworkError: -32008,
        AsyncClientNotAvailableError: -32009,
        YuqueError: -32603,  # JSON-RPC internal error
    }

    ERROR_MESSAGES: dict[type[Exception], dict[str, str]] = {
        AuthenticationError: {
            "title": "认证失败",
            "message": "API Token 无效或已过期",
            "suggestion": "请检查您的 API Token 配置。获取方式：\n"
            "1. 登录语雀 (https://www.yuque.com)\n"
            "2. 进入设置 -> 开发者设置\n"
            "3. 创建或复制您的 Personal Access Token\n"
            "4. 确保 Token 有足够的权限",
        },
        PermissionDeniedError: {
            "title": "权限不足",
            "message": "您没有权限执行此操作",
            "suggestion": "请检查：\n"
            "1. 您是否有访问该资源的权限\n"
            "2. Token 是否有相应的权限范围\n"
            "3. 资源是否设置为公开或您是否在团队中",
        },
        NotFoundError: {
            "title": "资源不存在",
            "message": "请求的资源未找到",
            "suggestion": "请确认：\n"
            "1. 资源 ID 或路径是否正确\n"
            "2. 资源是否已被删除\n"
            "3. 您是否有权限访问该资源",
        },
        InvalidArgumentError: {
            "title": "参数错误",
            "message": "请求参数无效",
            "suggestion": "请检查：\n"
            "1. 必需参数是否都已提供\n"
            "2. 参数格式是否正确\n"
            "3. 参数值是否在有效范围内",
        },
        ValidationError: {
            "title": "验证失败",
            "message": "请求数据验证失败",
            "suggestion": "请检查：\n"
            "1. 数据格式是否符合要求\n"
            "2. 字段值是否有效\n"
            "3. 必填字段是否完整",
        },
        RateLimitError: {
            "title": "请求限流",
            "message": "API 请求频率超限",
            "suggestion": "建议：\n1. 稍后重试\n2. 减少请求频率\n3. 使用缓存减少重复请求",
        },
        ServerError: {
            "title": "服务器错误",
            "message": "语雀服务器发生错误",
            "suggestion": "建议：\n"
            "1. 稍后重试\n"
            "2. 如果问题持续，请联系语雀支持\n"
            "3. 检查语雀服务状态",
        },
        NetworkError: {
            "title": "网络错误",
            "message": "网络连接失败",
            "suggestion": "请检查：\n"
            "1. 网络连接是否正常\n"
            "2. 是否能访问语雀服务\n"
            "3. 防火墙或代理设置",
        },
        AsyncClientNotAvailableError: {
            "title": "客户端错误",
            "message": "异步客户端不可用",
            "suggestion": "请使用 async_client() 方法创建异步客户端",
        },
    }

    def adapt_exception(self, error: Exception) -> MCPError:
        """Adapt a Yuque exception to an MCP error.

        Transforms Yuque-specific exceptions into MCP protocol errors
        with user-friendly messages and self-correction suggestions.

        Args:
            error: The exception to adapt.

        Returns:
            MCPError instance with appropriate code, message, and data.

        Example:
            ```python
            try:
                client.user.get_me()
            except AuthenticationError as e:
                mcp_error = adapter.adapt_exception(e)
                return mcp_error.to_tool_error()
            ```
        """
        error_code = self.ERROR_CODES.get(type(error), -32603)

        error_info = self.ERROR_MESSAGES.get(
            type(error),
            {
                "title": "未知错误",
                "message": str(error),
                "suggestion": "请检查错误信息并重试",
            },
        )

        error_message = self._format_error_message(error, error_info)
        error_data = self._build_error_data(error, error_info)

        return MCPError(
            code=error_code,
            message=error_message,
            data=error_data,
        )

        # Build error message
        error_message = self._format_error_message(error, error_info)

        # Build error data with suggestions
        error_data = self._build_error_data(error, error_info)

        return MCPError(
            code=error_code,
            message=error_message,
            data=error_data,
        )

    def _format_error_message(
        self,
        error: Exception,
        error_info: dict[str, str],
    ) -> str:
        """Format a user-friendly error message.

        Args:
            error: The original exception.
            error_info: Error information dict with title and message.

        Returns:
            Formatted error message string.
        """
        base_message = str(error) if str(error) else error_info["message"]

        if error_info.get("title"):
            return f"{error_info['title']}: {base_message}"
        return base_message

    def _build_error_data(
        self,
        error: Exception,
        error_info: dict[str, str],
    ) -> dict[str, Any]:
        """Build additional error data with suggestions.

        Args:
            error: The original exception.
            error_info: Error information dict with suggestions.

        Returns:
            Dictionary with error details and suggestions.
        """
        data: dict[str, Any] = {}

        if error_info.get("suggestion"):
            data["suggestion"] = error_info["suggestion"]

        if isinstance(error, YuqueError) and error.status_code:
            data["status_code"] = error.status_code

        if isinstance(error, RateLimitError) and error.retry_after is not None:
            data["retry_after"] = error.retry_after
            data["retry_after_human"] = f"{error.retry_after}秒"

        if isinstance(error, YuqueError) and error.response_data:
            data["response_data"] = error.response_data

        data["error_type"] = type(error).__name__

        return data

    def adapt_to_tool_error(self, error: Exception) -> dict[str, Any]:
        """Convenience method to adapt exception directly to tool error format.

        Args:
            error: The exception to adapt.

        Returns:
            MCP tool execution error dictionary.

        Example:
            ```python
            try:
                result = await some_operation()
            except Exception as e:
                return adapter.adapt_to_tool_error(e)
            ```
        """
        mcp_error = self.adapt_exception(error)
        return mcp_error.to_tool_error()


default_adapter = ErrorAdapter()


def adapt_exception(error: Exception) -> MCPError:
    """Adapt an exception to MCP error using default adapter.

    This is a convenience function that uses the global default adapter.

    Args:
        error: The exception to adapt.

    Returns:
        MCPError instance.

    Example:
        ```python
        from yuque.mcp.adapters import adapt_exception

        try:
            client.user.get_me()
        except AuthenticationError as e:
            mcp_error = adapt_exception(e)
            return mcp_error.to_tool_error()
        ```
    """
    return default_adapter.adapt_exception(error)


def adapt_error(error: Exception) -> dict[str, Any]:
    """Adapt an exception to MCP error response format.

    This function provides backward compatibility with the original
    adapt_error function signature.

    Args:
        error: The exception to adapt.

    Returns:
        MCP-formatted error response dictionary.

    Example:
        ```python
        from yuque.mcp.adapters import adapt_error

        try:
            # ... some operation
            pass
        except Exception as e:
            return adapt_error(e)
        ```
    """
    mcp_error = adapt_exception(error)
    return mcp_error.to_tool_error()
