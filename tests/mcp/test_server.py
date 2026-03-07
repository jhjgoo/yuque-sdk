"""Tests for MCP server implementation."""

from __future__ import annotations

import logging
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from yuque.mcp.server import MCPServer


@pytest.fixture
def mock_fastmcp():
    """Create a mock FastMCP instance."""
    mcp = MagicMock()
    mcp.run = MagicMock()
    mcp.run_stdio_async = AsyncMock()
    mcp.run_sse_async = AsyncMock()
    mcp.run_streamable_http_async = AsyncMock()
    mcp._tool_manager = MagicMock()
    mcp._tool_manager._tools = {}
    return mcp


@pytest.fixture
def mock_yuque_client():
    """Create a mock YuqueClient instance."""
    client = MagicMock()
    client.__aexit__ = AsyncMock()
    return client


@pytest.fixture(autouse=True)
def clear_env_token():
    """Clear YUQUE_TOKEN environment variable before each test."""
    original = os.environ.pop("YUQUE_TOKEN", None)
    yield
    if original is not None:
        os.environ["YUQUE_TOKEN"] = original


class TestMCPServerInit:
    """Tests for MCPServer initialization."""

    def test_init_with_explicit_token(self, mock_fastmcp, mock_yuque_client):
        """Test server initialization with explicit token parameter."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token-123")

            assert server._token == "test-token-123"

    def test_init_with_env_token(self, mock_fastmcp, mock_yuque_client):
        """Test server reads YUQUE_TOKEN from environment."""
        os.environ["YUQUE_TOKEN"] = "env-token-456"

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer()

            assert server._token == "env-token-456"

    def test_init_missing_token_raises_valueerror(self, mock_fastmcp, mock_yuque_client):
        """Test that missing token raises ValueError."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            with pytest.raises(ValueError) as exc_info:
                MCPServer()

            assert "Yuque API token is required" in str(exc_info.value)

    def test_custom_server_name(self, mock_fastmcp, mock_yuque_client):
        """Test custom name parameter is passed to FastMCP."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp) as mock_mcp_class,
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            MCPServer(token="test-token", name="custom-server-name")

            mock_mcp_class.assert_called_once()
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["name"] == "custom-server-name"

    def test_custom_instructions(self, mock_fastmcp, mock_yuque_client):
        """Test custom instructions parameter is passed to FastMCP."""
        custom_instructions = "Use this server to access my knowledge base."

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp) as mock_mcp_class,
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            MCPServer(token="test-token", instructions=custom_instructions)

            mock_mcp_class.assert_called_once()
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["instructions"] == custom_instructions

    def test_default_instructions_when_not_provided(self, mock_fastmcp, mock_yuque_client):
        """Test default instructions are used when not provided."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp) as mock_mcp_class,
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            MCPServer(token="test-token")

            mock_mcp_class.assert_called_once()
            call_kwargs = mock_mcp_class.call_args[1]
            assert "Yuque" in call_kwargs["instructions"]
            assert "documents" in call_kwargs["instructions"]

    def test_debug_mode_enabled(self, mock_fastmcp, mock_yuque_client):
        """Test debug mode configuration is passed to FastMCP."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp) as mock_mcp_class,
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            MCPServer(token="test-token", debug=True)

            mock_mcp_class.assert_called_once()
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["debug"] is True

    def test_log_level_configuration(self, mock_fastmcp, mock_yuque_client):
        """Test log level setup is passed to FastMCP."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp) as mock_mcp_class,
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            MCPServer(token="test-token", log_level="DEBUG")

            mock_mcp_class.assert_called_once()
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["log_level"] == "DEBUG"


class TestToolRegistration:
    """Tests for tool group registration."""

    def test_all_tool_groups_registered(self, mock_fastmcp, mock_yuque_client):
        """Test that all 5 tool groups are registered."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
            patch("yuque.mcp.server.register_user_tools") as mock_user,
            patch("yuque.mcp.server.register_doc_tools") as mock_doc,
            patch("yuque.mcp.server.register_repo_tools") as mock_repo,
            patch("yuque.mcp.server.register_search_tools") as mock_search,
            patch("yuque.mcp.server.register_group_tools") as mock_group,
        ):
            MCPServer(token="test-token")

            mock_user.assert_called_once_with(mock_fastmcp, mock_yuque_client)
            mock_doc.assert_called_once_with(mock_fastmcp, mock_yuque_client)
            mock_repo.assert_called_once_with(mock_fastmcp, mock_yuque_client)
            mock_search.assert_called_once_with(mock_fastmcp, mock_yuque_client)
            mock_group.assert_called_once_with(mock_fastmcp, mock_yuque_client)


class TestLogging:
    """Tests for logging configuration."""

    def test_stderr_logging_handler(self, mock_fastmcp, mock_yuque_client):
        """Test that logging is configured to use stderr."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server_logger = logging.getLogger("yuque.mcp.server")
            server_logger.handlers.clear()

            MCPServer(token="test-token")

            handlers = [h for h in server_logger.handlers if isinstance(h, logging.StreamHandler)]
            assert len(handlers) > 0
            stderr_handlers = [h for h in handlers if h.stream == sys.stderr]
            assert len(stderr_handlers) > 0

    def test_debug_mode_sets_debug_level(self, mock_fastmcp, mock_yuque_client):
        """Test that debug mode sets logging level to DEBUG."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server_logger = logging.getLogger("yuque.mcp.server")
            server_logger.handlers.clear()

            MCPServer(token="test-token", debug=True)

            assert server_logger.level == logging.DEBUG


class TestProperties:
    """Tests for server properties."""

    def test_client_property_returns_yuqueclient(self, mock_fastmcp, mock_yuque_client):
        """Test that client property returns the YuqueClient instance."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")

            assert server.client is mock_yuque_client

    def test_mcp_property_returns_fastmcp(self, mock_fastmcp, mock_yuque_client):
        """Test that mcp property returns the FastMCP instance."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")

            assert server.mcp is mock_fastmcp


class TestRunMethods:
    """Tests for server run methods."""

    def test_transport_default_stdio(self, mock_fastmcp, mock_yuque_client):
        """Test that default transport is stdio."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            server.run()

            mock_fastmcp.run.assert_called_once_with(transport="stdio")

    def test_run_method_calls_fastmcp_run(self, mock_fastmcp, mock_yuque_client):
        """Test that run() calls FastMCP.run()."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            server.run(transport="sse")

            mock_fastmcp.run.assert_called_once_with(transport="sse")

    def test_run_method_handles_exceptions(self, mock_fastmcp, mock_yuque_client):
        """Test that run() properly handles and re-raises exceptions."""
        mock_fastmcp.run.side_effect = RuntimeError("Server failed")

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")

            with pytest.raises(RuntimeError, match="Server failed"):
                server.run()

    @pytest.mark.asyncio
    async def test_start_async_calls_fastmcp_run_async(self, mock_fastmcp, mock_yuque_client):
        """Test that start_async() calls FastMCP.run_stdio_async()."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.start_async(transport="stdio")

            mock_fastmcp.run_stdio_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_async_sse_transport(self, mock_fastmcp, mock_yuque_client):
        """Test start_async with SSE transport."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.start_async(transport="sse")

            mock_fastmcp.run_sse_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_async_streamable_http_transport(self, mock_fastmcp, mock_yuque_client):
        """Test start_async with streamable-http transport."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.start_async(transport="streamable-http")

            mock_fastmcp.run_streamable_http_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_async_unknown_transport_raises_valueerror(
        self, mock_fastmcp, mock_yuque_client
    ):
        """Test start_async raises ValueError for unknown transport."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")

            with pytest.raises(ValueError, match="Unknown transport"):
                await server.start_async(transport="invalid")


class TestContextManagers:
    """Tests for context manager protocols."""

    def test_sync_context_manager_lifecycle(self, mock_fastmcp, mock_yuque_client):
        """Test synchronous context manager with __enter__ and __exit__."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            assert server._token == "test-token"

    @pytest.mark.asyncio
    async def test_async_context_manager_lifecycle(self, mock_fastmcp, mock_yuque_client):
        """Test async context manager lifecycle with __aenter__ and __aexit__."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            async with MCPServer(token="test-token") as server:
                assert server._token == "test-token"

    @pytest.mark.asyncio
    async def test_async_context_manager_calls_client_aexit(self, mock_fastmcp, mock_yuque_client):
        """Test that __aexit__ calls client's __aexit__ if available."""
        mock_yuque_client.__aexit__ = AsyncMock()

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.__aenter__()
            await server.__aexit__(None, None, None)

            mock_yuque_client.__aexit__.assert_called_once_with(None, None, None)

    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception(self, mock_fastmcp, mock_yuque_client):
        """Test __aexit__ properly passes exception info to client."""
        mock_yuque_client.__aexit__ = AsyncMock()

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.__aenter__()

            exc_type = RuntimeError
            exc_val = RuntimeError("Test error")
            exc_tb = None

            await server.__aexit__(exc_type, exc_val, exc_tb)

            mock_yuque_client.__aexit__.assert_called_once_with(exc_type, exc_val, exc_tb)

    @pytest.mark.asyncio
    async def test_async_context_manager_without_client_aexit(
        self, mock_fastmcp, mock_yuque_client
    ):
        """Test __aexit__ handles client without __aexit__ method."""
        delattr(mock_yuque_client, "__aexit__")

        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            await server.__aenter__()
            await server.__aexit__(None, None, None)


class TestRegisterTools:
    """Tests for register_tools method."""

    def test_register_tools_logs_info(self, mock_fastmcp, mock_yuque_client):
        """Test that register_tools logs an info message."""
        with (
            patch("yuque.mcp.server.FastMCP", return_value=mock_fastmcp),
            patch("yuque.mcp.server.YuqueClient", return_value=mock_yuque_client),
        ):
            server = MCPServer(token="test-token")
            server.register_tools()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
