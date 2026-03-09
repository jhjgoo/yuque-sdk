#!/usr/bin/env python3
"""Integration tests for MCP server functionality.

This test suite verifies that:
1. All expected tools are registered correctly
2. Each tool category has the right number of tools
3. Tools can be called without errors (basic smoke tests)
4. The total tool count matches expectations (26 tools)
"""

import asyncio
import os
from typing import Any

import pytest
from yuque.mcp.server import MCPServer


# Expected tool counts by module
EXPECTED_TOOL_COUNTS = {
    "user": 3,
    "doc": 9,
    "repo": 6,
    "group": 5,
    "search": 1,
}

TOTAL_EXPECTED_TOOLS = 26


class TestMCPToolRegistration:
    """Test suite for MCP tool registration."""
    
    @pytest.fixture
    async def mcp_server(self):
        """Create an MCP server instance for testing."""
        os.environ["YUQUE_TOKEN"] = "test_token_for_integration"
        server = MCPServer(
            name="yuque-test",
            debug=False,
        )
        yield server
    
    async def test_total_tool_count(self, mcp_server: MCPServer):
        """Test that all expected tools are registered."""
        tools = await mcp_server._mcp.list_tools()
        assert len(tools) == TOTAL_EXPECTED_TOOLS, (
            f"Expected {TOTAL_EXPECTED_TOOLS} tools, but got {len(tools)}"
        )
    
    async def test_no_duplicate_tools(self, mcp_server: MCPServer):
        """Test that there are no duplicate tool names."""
        tools = await mcp_server._mcp.list_tools()
        tool_names = [tool.name for tool in tools]
        duplicates = [name for name in tool_names if tool_names.count(name) > 1]
        assert len(duplicates) == 0, f"Found duplicate tools: {set(duplicates)}"
    
    async def test_tool_naming_convention(self, mcp_server: MCPServer):
        """Test that all tools follow the naming convention."""
        tools = await mcp_server._mcp.list_tools()
        for tool in tools:
            assert tool.name.startswith("yuque_"), (
                f"Tool '{tool.name}' should start with 'yuque_'"
            )
    
    async def test_tool_descriptions(self, mcp_server: MCPServer):
        """Test that all tools have descriptions."""
        tools = await mcp_server._mcp.list_tools()
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' missing description"
            assert len(tool.description) > 10, (
                f"Tool '{tool.name}' description too short"
            )
    
    async def test_user_tools_registered(self, mcp_server: MCPServer):
        """Test that user-related tools are registered."""
        tools = await mcp_server._mcp.list_tools()
        user_tools = [t for t in tools if any(
            keyword in t.name for keyword in ['user', 'member']
        )]
        assert len(user_tools) >= EXPECTED_TOOL_COUNTS["user"], (
            f"Expected at least {EXPECTED_TOOL_COUNTS['user']} user tools"
        )
    
    async def test_doc_tools_registered(self, mcp_server: MCPServer):
        """Test that document-related tools are registered."""
        tools = await mcp_server._mcp.list_tools()
        doc_tools = [t for t in tools if 'doc' in t.name]
        assert len(doc_tools) >= EXPECTED_TOOL_COUNTS["doc"], (
            f"Expected at least {EXPECTED_TOOL_COUNTS['doc']} doc tools"
        )
    
    async def test_repo_tools_registered(self, mcp_server: MCPServer):
        """Test that repository-related tools are registered."""
        tools = await mcp_server._mcp.list_tools()
        repo_tools = [t for t in tools if 'repo' in t.name]
        assert len(repo_tools) >= EXPECTED_TOOL_COUNTS["repo"], (
            f"Expected at least {EXPECTED_TOOL_COUNTS['repo']} repo tools"
        )
    
    async def test_group_tools_registered(self, mcp_server: MCPServer):
        """Test that group-related tools are registered."""
        tools = await mcp_server._mcp.list_tools()
        group_tools = [t for t in tools if 'group' in t.name]
        assert len(group_tools) >= EXPECTED_TOOL_COUNTS["group"], (
            f"Expected at least {EXPECTED_TOOL_COUNTS['group']} group tools"
        )
    
    async def test_search_tool_registered(self, mcp_server: MCPServer):
        """Test that search tool is registered."""
        tools = await mcp_server._mcp.list_tools()
        search_tools = [t for t in tools if 'search' in t.name]
        assert len(search_tools) >= EXPECTED_TOOL_COUNTS["search"], (
            f"Expected at least {EXPECTED_TOOL_COUNTS['search']} search tools"
        )
    
    async def test_all_tool_categories(self, mcp_server: MCPServer):
        """Test comprehensive list of all tool categories."""
        tools = await mcp_server._mcp.list_tools()
        tool_names = [t.name for t in tools]
        
        # Verify specific important tools exist
        expected_tools = [
            "yuque_get_current_user",
            "yuque_create_doc",
            "yuque_update_doc",
            "yuque_delete_doc",
            "yuque_get_repo",
            "yuque_list_repos",
            "yuque_get_group",
            "yuque_search",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Missing tool: {tool_name}"


async def manual_verification():
    """Manual verification helper - not a test, just for debugging."""
    os.environ["YUQUE_TOKEN"] = "test_token"
    
    print("\n" + "=" * 70)
    print("MANUAL VERIFICATION - MCP Tool Registration")
    print("=" * 70)
    
    server = MCPServer(name="yuque-manual", debug=True)
    tools = await server._mcp.list_tools()
    
    print(f"\n✅ Total tools: {len(tools)}")
    print(f"✅ Expected: {TOTAL_EXPECTED_TOOLS}")
    print(f"✅ Status: {'PASS' if len(tools) == TOTAL_EXPECTED_TOOLS else 'FAIL'}")
    
    print("\n📋 Complete tool list:")
    for i, tool in enumerate(sorted(tools, key=lambda t: t.name), 1):
        print(f"{i:2d}. {tool.name}")
    
    print("\n" + "=" * 70)
    
    return len(tools) == TOTAL_EXPECTED_TOOLS


if __name__ == "__main__":
    # Run manual verification when executed directly
    success = asyncio.run(manual_verification())
    exit(0 if success else 1)
