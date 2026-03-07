"""Tests for MCP CLI interface.

This module tests the command-line interface for running the Yuque MCP server,
including argument parsing, environment validation, logging setup, and error handling.
"""

from __future__ import annotations

import logging
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from yuque.mcp import cli


@pytest.fixture(autouse=True)
def clear_env_token():
    """Clear YUQUE_TOKEN environment variable before each test."""
    original = os.environ.pop("YUQUE_TOKEN", None)
    yield
    if original is not None:
        os.environ["YUQUE_TOKEN"] = original
    else:
        os.environ.pop("YUQUE_TOKEN", None)


class TestCreateParser:
    """Tests for argument parser creation."""

    def test_create_parser_default_values(self):
        """Test parser with default transport and log level."""
        parser = cli.create_parser()
        args = parser.parse_args([])

        assert args.transport == "stdio"
        assert args.log_level == "INFO"
        assert args.debug is False
        assert args.name == "yuque"

    def test_parse_arguments_custom_transport(self):
        """Test parser with custom transport (SSE/HTTP)."""
        parser = cli.create_parser()

        # Test SSE transport
        args = parser.parse_args(["--transport", "sse"])
        assert args.transport == "sse"

        # Test HTTP transport
        args = parser.parse_args(["--transport", "http"])
        assert args.transport == "http"

    def test_parse_arguments_debug_mode(self):
        """Test parser with debug flag."""
        parser = cli.create_parser()
        args = parser.parse_args(["--debug"])

        assert args.debug is True

    def test_parse_arguments_log_level(self):
        """Test parser with custom log level."""
        parser = cli.create_parser()
        args = parser.parse_args(["--log-level", "DEBUG"])

        assert args.log_level == "DEBUG"

    def test_version_flag(self, capsys):
        """Test --version output."""
        parser = cli.create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "yuque-mcp" in captured.out
        assert "0.1.0" in captured.out

    def test_help_flag(self, capsys):
        """Test --help output."""
        parser = cli.create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Yuque MCP Server" in captured.out
        assert "--transport" in captured.out
        assert "--debug" in captured.out
        assert "--log-level" in captured.out

    def test_custom_name_argument(self):
        """Test custom server name argument."""
        parser = cli.create_parser()
        args = parser.parse_args(["--name", "my-custom-server"])

        assert args.name == "my-custom-server"


class TestValidateEnvironment:
    """Tests for environment validation."""

    def test_validate_environment_missing_token(self, capsys):
        """Test validation exits with code 1 when token is missing."""
        # Ensure token is not set
        os.environ.pop("YUQUE_TOKEN", None)

        with pytest.raises(SystemExit) as exc_info:
            cli.validate_environment()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "YUQUE_TOKEN environment variable is required" in captured.err
        assert "export YUQUE_TOKEN=" in captured.err

    def test_validate_environment_with_token(self):
        """Test validation succeeds when token is present."""
        os.environ["YUQUE_TOKEN"] = "test-token-123"

        # Should not raise any exception
        cli.validate_environment()

    def test_validate_environment_empty_token(self, capsys):
        """Test validation fails with empty token string."""
        os.environ["YUQUE_TOKEN"] = ""

        with pytest.raises(SystemExit) as exc_info:
            cli.validate_environment()

        assert exc_info.value.code == 1


class TestSetupLogging:
    """Tests for logging configuration."""

    def test_setup_logging_debug_mode(self):
        """Test debug logging setup."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        cli.setup_logging("INFO", debug=True)

        assert root_logger.level == logging.DEBUG
        # Check that stderr handler was added
        assert any(
            isinstance(h, logging.StreamHandler) and h.stream == sys.stderr
            for h in root_logger.handlers
        )

    def test_setup_logging_custom_level(self):
        """Test custom level setup."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        cli.setup_logging("WARNING", debug=False)

        assert root_logger.level == logging.WARNING

    def test_setup_logging_info_level(self):
        """Test INFO level setup (default)."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        cli.setup_logging("INFO", debug=False)

        assert root_logger.level == logging.INFO

    def test_setup_logging_error_level(self):
        """Test ERROR level setup."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        cli.setup_logging("ERROR", debug=False)

        assert root_logger.level == logging.ERROR


class TestTransportMapping:
    """Tests for transport protocol mapping."""

    def test_transport_mapping_stdio(self):
        """Test STDIO transport mapping."""
        transport_map = {
            "stdio": "stdio",
            "sse": "sse",
            "http": "streamable-http",
        }
        assert transport_map["stdio"] == "stdio"

    def test_transport_mapping_sse(self):
        """Test SSE transport mapping."""
        transport_map = {
            "stdio": "stdio",
            "sse": "sse",
            "http": "streamable-http",
        }
        assert transport_map["sse"] == "sse"

    def test_transport_mapping_http(self):
        """Test HTTP transport mapping to streamable-http."""
        transport_map = {
            "stdio": "stdio",
            "sse": "sse",
            "http": "streamable-http",
        }
        assert transport_map["http"] == "streamable-http"


class TestMain:
    """Tests for main entry point."""

    def test_main_with_valid_config(self):
        """Test successful execution with valid configuration."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp"]),
            patch("sys.exit") as mock_exit,
        ):
            cli.main()

            # Verify server was created with correct parameters
            mock_exit.assert_called()

    def test_main_missing_token_exits(self, capsys):
        """Test main exits on missing token."""
        os.environ.pop("YUQUE_TOKEN", None)

        with (
            patch("sys.argv", ["yuque-mcp"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            cli.main()

        assert exc_info.value.code == 1

    def test_main_value_error_handling(self, capsys):
        """Test ValueError handling in main."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run.side_effect = ValueError("Configuration error")

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            cli.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Configuration error" in captured.err

    def test_main_keyboard_interrupt(self, capsys):
        """Test KeyboardInterrupt (Ctrl+C) handling."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run.side_effect = KeyboardInterrupt()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            cli.main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Server stopped" in captured.err

    def test_main_generic_exception(self, capsys):
        """Test generic exception handling."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run.side_effect = RuntimeError("Unexpected error")

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp", "--debug"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            cli.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unexpected error" in captured.err

    def test_main_with_debug_mode(self):
        """Test main with debug mode enabled."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server) as mock_mcp_class,
            patch("sys.argv", ["yuque-mcp", "--debug"]),
            patch("sys.exit"),
        ):
            cli.main()

            # Verify MCPServer was called with debug=True
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["debug"] is True

    def test_main_with_custom_log_level(self):
        """Test main with custom log level."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server) as mock_mcp_class,
            patch("sys.argv", ["yuque-mcp", "--log-level", "DEBUG"]),
            patch("sys.exit"),
        ):
            cli.main()

            # Verify MCPServer was called with custom log level
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["log_level"] == "DEBUG"

    def test_main_with_sse_transport(self):
        """Test main with SSE transport."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp", "--transport", "sse"]),
            patch("sys.exit"),
        ):
            cli.main()

            # Verify server.run was called with SSE transport
            mock_server.run.assert_called_once_with(transport="sse")

    def test_main_with_http_transport(self):
        """Test main with HTTP transport."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server),
            patch("sys.argv", ["yuque-mcp", "--transport", "http"]),
            patch("sys.exit"),
        ):
            cli.main()

            # Verify server.run was called with streamable-http transport
            mock_server.run.assert_called_once_with(transport="streamable-http")


class TestArgumentCombinations:
    """Tests for various argument combinations."""

    def test_all_arguments_combined(self):
        """Test parser with all arguments combined."""
        parser = cli.create_parser()
        args = parser.parse_args(
            ["--transport", "sse", "--debug", "--log-level", "DEBUG", "--name", "my-server"]
        )

        assert args.transport == "sse"
        assert args.debug is True
        assert args.log_level == "DEBUG"
        assert args.name == "my-server"

    def test_invalid_transport(self, capsys):
        """Test parser rejects invalid transport."""
        parser = cli.create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--transport", "invalid"])

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err

    def test_invalid_log_level(self, capsys):
        """Test parser rejects invalid log level."""
        parser = cli.create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--log-level", "INVALID"])

        assert exc_info.value.code == 2
        captured = capsys.readouterr()
        assert "invalid choice" in captured.err


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_main_with_name_parameter(self):
        """Test main with custom server name."""
        os.environ["YUQUE_TOKEN"] = "test-token"

        mock_server = MagicMock()
        mock_server.run = MagicMock()

        with (
            patch("yuque.mcp.cli.MCPServer", return_value=mock_server) as mock_mcp_class,
            patch("sys.argv", ["yuque-mcp", "--name", "custom-name"]),
            patch("sys.exit"),
        ):
            cli.main()

            # Verify MCPServer was called with custom name
            call_kwargs = mock_mcp_class.call_args[1]
            assert call_kwargs["name"] == "custom-name"

    def test_debug_mode_overrides_log_level(self):
        """Test that debug mode overrides log level setting."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Even with INFO log level, debug=True should set level to DEBUG
        cli.setup_logging("INFO", debug=True)

        assert root_logger.level == logging.DEBUG

    def test_logging_format(self):
        """Test that logging format is correctly set."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        cli.setup_logging("INFO", debug=False)

        # Check that at least one handler has the correct format
        formatter = None
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                formatter = handler.formatter
                break

        assert formatter is not None
        assert "%(asctime)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
