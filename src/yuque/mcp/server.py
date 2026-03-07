"""MCP server implementation for Yuque."""

from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING, Any

from mcp.server.fastmcp import FastMCP

from ..client import YuqueClient
from .tools.doc import register_doc_tools
from .tools.group import register_group_tools
from .tools.repo import register_repo_tools
from .tools.search import register_search_tools
from .tools.user import register_user_tools

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for exposing Yuque API to AI assistants.

    This server implements the Model Context Protocol and provides
    tools for interacting with Yuque documents, repositories, and users.

    The server uses FastMCP from the MCP Python SDK and supports:
    - STDIO transport (default)
    - Environment variable configuration
    - Context manager protocol
    - Structured logging

    Args:
        token: Yuque API token for authentication. If not provided,
            will read from YUQUE_TOKEN environment variable.
        name: Server name for MCP identification (default: "yuque").
        instructions: Human-readable instructions for using the server.
        debug: Enable debug mode (default: False).
        log_level: Logging level (default: "INFO").

    Example:
        ```python
        # Using environment variable
        server = MCPServer()
        server.run()

        # With explicit token
        server = MCPServer(token="your-token")
        server.run()

        # As context manager
        async with MCPServer() as server:
            await server.start()
        ```
    """

    def __init__(
        self,
        token: str | None = None,
        name: str = "yuque",
        instructions: str | None = None,
        debug: bool = False,
        log_level: str = "INFO",
    ) -> None:
        """Initialize the MCP server."""
        self._setup_logging(log_level, debug)

        self._token = token or os.getenv("YUQUE_TOKEN")
        if not self._token:
            raise ValueError(
                "Yuque API token is required. "
                "Provide it via the 'token' parameter or set YUQUE_TOKEN environment variable."
            )

        if instructions is None:
            instructions = (
                "This server provides access to Yuque documents, repositories, and users. "
                "Use the available tools to interact with Yuque API."
            )

        self._mcp = FastMCP(
            name=name,
            instructions=instructions,
            debug=debug,
            log_level=log_level,
        )

        self._client = YuqueClient(token=self._token)

        register_user_tools(self._mcp, self._client)
        register_doc_tools(self._mcp, self._client)
        register_repo_tools(self._mcp, self._client)
        register_search_tools(self._mcp, self._client)
        register_group_tools(self._mcp, self._client)

        logger.info(f"Initialized MCP server '{name}' with Yuque client")

    def _setup_logging(self, log_level: str, debug: bool) -> None:
        """Configure logging for the MCP server.

        MCP servers should log to stderr to avoid interfering with
        STDIO transport communication.

        Args:
            log_level: Logging level string.
            debug: Whether to enable debug mode.
        """
        level = logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)

        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        logger.setLevel(level)
        logger.addHandler(handler)

    @property
    def client(self) -> YuqueClient:
        """Get the underlying Yuque client.

        Returns:
            The YuqueClient instance used by this server.
        """
        return self._client

    @property
    def mcp(self) -> FastMCP:
        """Get the underlying FastMCP instance.

        Returns:
            The FastMCP instance used by this server.
        """
        return self._mcp

    def run(self, transport: str = "stdio") -> None:
        """Start the MCP server with the specified transport.

        This is the main entry point for running the server.
        For STDIO transport (default), it will listen for MCP messages
        on stdin and write responses to stdout.

        Args:
            transport: Transport protocol to use. Options:
                - "stdio": Standard input/output (default, for CLI usage)
                - "sse": Server-Sent Events (for HTTP)
                - "streamable-http": Streamable HTTP (for HTTP)

        Example:
            ```python
            server = MCPServer()
            server.run()  # Starts STDIO server
            ```
        """
        logger.info(f"Starting MCP server with {transport} transport")
        try:
            self._mcp.run(transport=transport)
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise

    async def start_async(self, transport: str = "stdio") -> None:
        """Asynchronously start the MCP server.

        This method is useful when you want to run the server
        within an async context.

        Args:
            transport: Transport protocol to use.

        Note:
            For STDIO transport, this will run indefinitely until
            the process is terminated.
        """
        logger.info(f"Starting async MCP server with {transport} transport")
        if transport == "stdio":
            await self._mcp.run_stdio_async()
        elif transport == "sse":
            await self._mcp.run_sse_async()
        elif transport == "streamable-http":
            await self._mcp.run_streamable_http_async()
        else:
            raise ValueError(f"Unknown transport: {transport}")

    async def __aenter__(self) -> MCPServer:
        """Enter async context manager.

        Returns:
            The MCPServer instance.
        """
        logger.debug("Entering async context")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context manager.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Exception traceback if an error occurred.
        """
        logger.debug("Exiting async context")
        if hasattr(self._client, "__aexit__"):
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def register_tools(self) -> None:
        """Register all available MCP tools.

        This method should be called after initialization to register
        all tools that expose Yuque API functionality.

        Note:
            Tool implementations are in the tools module and will be
            registered using the @mcp.tool() decorator.
        """
        logger.info("Registering MCP tools")
