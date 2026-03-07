"""MCP (Model Context Protocol) server integration for Yuque.

This module provides MCP server functionality for exposing Yuque API
through the Model Context Protocol, enabling AI assistants to interact
with Yuque documents, repositories, and users.

Example:
    ```python
    from yuque.mcp import MCPServer

    server = MCPServer(token="your-api-token")
    server.run()
    ```
"""

from __future__ import annotations

from .server import MCPServer

__version__ = "0.1.0"

__all__ = [
    "MCPServer",
]
