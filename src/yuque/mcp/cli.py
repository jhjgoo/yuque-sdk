"""Command-line interface for Yuque MCP server.

This module provides the CLI entry point for running the Yuque MCP server.
It supports multiple transport modes and configuration options.

Usage:
    yuque-mcp                           # Start server (STDIO mode)
    yuque-mcp --transport stdio         # Explicit STDIO mode
    yuque-mcp --transport sse           # SSE transport (requires HTTP)
    yuque-mcp --transport http          # HTTP transport
    yuque-mcp --debug                   # Enable debug mode
    yuque-mcp --log-level DEBUG         # Set log level
    yuque-mcp --version                 # Show version
    yuque-mcp --help                    # Show help
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import NoReturn

from . import __version__
from .server import MCPServer

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="yuque-mcp",
        description="Yuque MCP Server - Expose Yuque API to AI assistants via MCP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           Start server in STDIO mode (default)
  %(prog)s --transport sse           Start server with SSE transport
  %(prog)s --transport http          Start server with HTTP transport
  %(prog)s --debug                   Enable debug mode with verbose logging
  %(prog)s --log-level DEBUG         Set specific log level

Environment Variables:
  YUQUE_TOKEN                        Yuque API token (required)

For more information, visit:
  https://www.yuque.com/yuque/developer/api
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--name",
        default="yuque",
        help="Server name for MCP identification (default: yuque)",
    )

    return parser


def validate_environment() -> None:
    """Validate that required environment variables are set.

    Raises:
        SystemExit: If YUQUE_TOKEN is not set.
    """
    if not os.getenv("YUQUE_TOKEN"):
        print(
            "Error: YUQUE_TOKEN environment variable is required.",
            file=sys.stderr,
        )
        print(
            "\nPlease set your Yuque API token:",
            file=sys.stderr,
        )
        print(
            "  export YUQUE_TOKEN='your-api-token'",
            file=sys.stderr,
        )
        print(
            "\nTo get your API token:",
            file=sys.stderr,
        )
        print(
            "  1. Log in to https://www.yuque.com",
            file=sys.stderr,
        )
        print(
            "  2. Go to Settings > Developer Settings",
            file=sys.stderr,
        )
        print(
            "  3. Create a new Personal Access Token",
            file=sys.stderr,
        )
        sys.exit(1)


def setup_logging(log_level: str, debug: bool) -> None:
    """Configure logging for the CLI.

    Args:
        log_level: Logging level string.
        debug: Whether to enable debug mode.
    """
    level = logging.DEBUG if debug else getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )

    if debug:
        logger.debug("Debug mode enabled")


def main() -> NoReturn:
    """Main entry point for the CLI.

    This function parses command-line arguments and starts the MCP server.

    Returns:
        Never returns (calls sys.exit).
    """
    parser = create_parser()
    args = parser.parse_args()

    validate_environment()
    setup_logging(args.log_level, args.debug)

    transport_map = {
        "stdio": "stdio",
        "sse": "sse",
        "http": "streamable-http",
    }
    transport = transport_map[args.transport]

    logger.info(f"Starting Yuque MCP server v{__version__}")
    logger.info(f"Transport: {transport}")
    logger.info(f"Debug mode: {args.debug}")
    logger.info(f"Log level: {args.log_level}")

    try:
        server = MCPServer(
            name=args.name,
            debug=args.debug,
            log_level=args.log_level,
        )

        logger.info(f"Running server with {transport} transport...")
        server.run(transport=transport)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\nServer stopped.", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
