"""
Tests for the Yuque MCP Skill Executor.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add skills directory to path for import
SKILL_DIR = Path(__file__).parent.parent.parent / "skills" / "yuque"
sys.path.insert(0, str(SKILL_DIR))


class TestExecutorModule:
    """Test executor module imports and structure."""

    def test_skill_directory_exists(self):
        """Skill directory should exist."""
        assert SKILL_DIR.exists()

    def test_skill_files_exist(self):
        """All required skill files should exist."""
        required_files = ["SKILL.md", "executor.py", "mcp-config.json", "package.json"]
        for filename in required_files:
            assert (SKILL_DIR / filename).exists(), f"Missing: {filename}"

    def test_mcp_config_valid_json(self):
        """mcp-config.json should be valid JSON."""
        config_path = SKILL_DIR / "mcp-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert "name" in config
        assert "command" in config
        assert config["command"] == "uvx"
        assert "args" in config
        assert "yuque-sdk" in config["args"]

    def test_package_json_valid(self):
        """package.json should be valid JSON with required fields."""
        package_path = SKILL_DIR / "package.json"
        with open(package_path) as f:
            package = json.load(f)

        assert "name" in package
        assert "version" in package


class TestExecutorFunctions:
    """Test executor async functions with mocked MCP client."""

    @pytest.fixture
    def mock_config(self):
        """Sample server config for testing."""
        return {
            "name": "yuque",
            "command": "uvx",
            "args": ["yuque-sdk"],
            "env": {"YUQUE_TOKEN": "test-token"},
        }

    @pytest.fixture
    def mock_tool(self):
        """Mock MCP tool object."""
        tool = MagicMock()
        tool.name = "yuque_get_current_user"
        tool.description = "Get current user info"
        tool.inputSchema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        return tool

    @pytest.mark.asyncio
    async def test_list_tools_from_server(self, mock_config, mock_tool):
        """Test listing tools from MCP server."""
        # Import the module
        import executor

        # Mock the MCP client
        mock_response = MagicMock()
        mock_response.tools = [mock_tool]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_response)

        with patch.object(executor, "stdio_client") as mock_stdio:
            with patch.object(executor, "ClientSession") as mock_client_session:
                # Setup async context managers
                mock_stdio.return_value.__aenter__ = AsyncMock(
                    return_value=(MagicMock(), MagicMock())
                )
                mock_stdio.return_value.__aexit__ = AsyncMock()

                mock_client_session.return_value.__aenter__ = AsyncMock(
                    return_value=mock_session
                )
                mock_client_session.return_value.__aexit__ = AsyncMock()

                result = await executor.list_tools_from_server(mock_config)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "yuque_get_current_user"
        assert result[0]["description"] == "Get current user info"

    @pytest.mark.asyncio
    async def test_describe_tool_from_server(self, mock_config, mock_tool):
        """Test describing a specific tool."""
        import executor

        mock_response = MagicMock()
        mock_response.tools = [mock_tool]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_response)

        with patch.object(executor, "stdio_client") as mock_stdio:
            with patch.object(executor, "ClientSession") as mock_client_session:
                mock_stdio.return_value.__aenter__ = AsyncMock(
                    return_value=(MagicMock(), MagicMock())
                )
                mock_stdio.return_value.__aexit__ = AsyncMock()

                mock_client_session.return_value.__aenter__ = AsyncMock(
                    return_value=mock_session
                )
                mock_client_session.return_value.__aexit__ = AsyncMock()

                result = await executor.describe_tool_from_server(
                    mock_config, "yuque_get_current_user"
                )

        assert result is not None
        assert result["name"] == "yuque_get_current_user"
        assert "inputSchema" in result

    @pytest.mark.asyncio
    async def test_describe_tool_not_found(self, mock_config, mock_tool):
        """Test describing a non-existent tool returns None."""
        import executor

        mock_response = MagicMock()
        mock_response.tools = [mock_tool]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_response)

        with patch.object(executor, "stdio_client") as mock_stdio:
            with patch.object(executor, "ClientSession") as mock_client_session:
                mock_stdio.return_value.__aenter__ = AsyncMock(
                    return_value=(MagicMock(), MagicMock())
                )
                mock_stdio.return_value.__aexit__ = AsyncMock()

                mock_client_session.return_value.__aenter__ = AsyncMock(
                    return_value=mock_session
                )
                mock_client_session.return_value.__aexit__ = AsyncMock()

                result = await executor.describe_tool_from_server(
                    mock_config, "non_existent_tool"
                )

        assert result is None

    @pytest.mark.asyncio
    async def test_call_tool_on_server(self, mock_config):
        """Test calling a tool on MCP server."""
        import executor

        mock_content = MagicMock()
        mock_content.text = '{"id": 123, "name": "test_user"}'

        mock_response = MagicMock()
        mock_response.content = [mock_content]

        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.call_tool = AsyncMock(return_value=mock_response)

        with patch.object(executor, "stdio_client") as mock_stdio:
            with patch.object(executor, "ClientSession") as mock_client_session:
                mock_stdio.return_value.__aenter__ = AsyncMock(
                    return_value=(MagicMock(), MagicMock())
                )
                mock_stdio.return_value.__aexit__ = AsyncMock()

                mock_client_session.return_value.__aenter__ = AsyncMock(
                    return_value=mock_session
                )
                mock_client_session.return_value.__aexit__ = AsyncMock()

                result = await executor.call_tool_on_server(
                    mock_config, "yuque_get_current_user", {}
                )

        assert result is not None
        mock_session.call_tool.assert_called_once_with("yuque_get_current_user", {})


class TestSkillMarkdown:
    """Test SKILL.md content."""

    def test_skill_md_has_frontmatter(self):
        """SKILL.md should have valid frontmatter."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text()

        assert content.startswith("---")
        # Check frontmatter fields
        assert "name: yuque" in content
        assert "description:" in content
        assert "version:" in content

    def test_skill_md_has_tools_list(self):
        """SKILL.md should list available tools."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text()

        # Check for tool categories
        assert "User Tools" in content
        assert "Document Tools" in content
        assert "Repository Tools" in content
        assert "Group Tools" in content
        assert "Search Tools" in content

        # Check for specific tools
        assert "yuque_get_current_user" in content
        assert "yuque_create_doc" in content
        assert "yuque_search" in content

    def test_skill_md_has_usage_examples(self):
        """SKILL.md should have usage examples."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text()

        assert "## Examples" in content
        assert "executor.py --call" in content
        assert "executor.py --describe" in content
        assert "executor.py --list" in content


class TestCLIParsing:
    """Test CLI argument parsing."""

    def test_argparse_list_flag(self):
        """Test --list flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--call", help="JSON tool call")
        parser.add_argument("--describe", help="Tool name")
        parser.add_argument("--list", action="store_true")

        args = parser.parse_args(["--list"])
        assert args.list is True
        assert args.call is None
        assert args.describe is None

    def test_argparse_call_flag(self):
        """Test --call flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--call", help="JSON tool call")
        parser.add_argument("--describe", help="Tool name")
        parser.add_argument("--list", action="store_true")

        call_json = '{"tool": "yuque_search", "arguments": {"query": "test"}}'
        args = parser.parse_args(["--call", call_json])

        assert args.call == call_json
        assert args.list is False

        # Verify JSON is parseable
        parsed = json.loads(args.call)
        assert parsed["tool"] == "yuque_search"

    def test_argparse_describe_flag(self):
        """Test --describe flag parsing."""
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--call", help="JSON tool call")
        parser.add_argument("--describe", help="Tool name")
        parser.add_argument("--list", action="store_true")

        args = parser.parse_args(["--describe", "yuque_get_doc"])
        assert args.describe == "yuque_get_doc"
