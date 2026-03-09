---
name: yuque
description: Dynamic access to Yuque MCP server (26 tools for docs, repos, groups, search)
version: 1.0.0
homepage: https://github.com/jhjgoo/yuque-sdk
metadata: { "openclaw": { "emoji": "📚", "homepage": "https://github.com/jhjgoo/yuque-sdk", "requires": { "bins": ["uvx", "python3"], "env": ["YUQUE_TOKEN"] }, "primaryEnv": "YUQUE_TOKEN" } }
---

# Yuque Skill

This skill provides dynamic access to the Yuque MCP server without loading all tool definitions into context.

## Context Efficiency

Traditional MCP approach:
- All 26 tools loaded at startup
- Estimated context: ~15k tokens

This skill approach:
- Metadata only: ~500 tokens
- Full instructions (when used): ~2k tokens
- Tool execution: 0 tokens (runs externally)

**Savings: ~85% reduction in typical usage**

## How This Works

Instead of loading all MCP tool definitions upfront, this skill:
1. Tells you what tools are available (just names and brief descriptions)
2. You decide which tool to call based on the user's request
3. Generate a JSON command to invoke the tool
4. The executor handles the actual MCP communication

## Available Tools

### User Tools
- `yuque_get_current_user`: Get current authenticated user info
- `yuque_get_user`: Get user by login/id
- `yuque_get_user_groups`: Get groups for a user

### Document Tools
- `yuque_get_doc`: Get document by slug/id
- `yuque_create_doc`: Create new document
- `yuque_update_doc`: Update existing document
- `yuque_delete_doc`: Delete document
- `yuque_list_docs`: List documents in a repository
- `yuque_get_doc_history`: Get document revision history
- `yuque_export_doc`: Export document to markdown/html
- `yuque_batch_get_docs`: Batch get multiple documents
- `yuque_move_doc`: Move document to another location

### Repository Tools
- `yuque_get_repo`: Get repository details
- `yuque_list_repos`: List repositories
- `yuque_get_repo_toc`: Get repository table of contents
- `yuque_create_repo`: Create new repository
- `yuque_update_repo`: Update repository settings
- `yuque_delete_repo`: Delete repository

### Group Tools
- `yuque_get_group`: Get group/team info
- `yuque_get_group_repos`: List repositories in a group
- `yuque_get_group_members`: List group members
- `yuque_create_group`: Create new group
- `yuque_update_group`: Update group settings
- `yuque_delete_group`: Delete group

### Search Tools
- `yuque_search`: Search across docs, repos, groups

## Usage Pattern

When the user's request matches this skill's capabilities:

**Step 1: Identify the right tool** from the list above

**Step 2: Generate a tool call** in this JSON format:

```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Step 3: Execute via bash:**

```bash
cd $SKILL_DIR
python executor.py --call 'YOUR_JSON_HERE'
```

IMPORTANT: Replace $SKILL_DIR with the actual discovered path of this skill directory.

## Getting Tool Details

If you need detailed information about a specific tool's parameters:

```bash
cd $SKILL_DIR
python executor.py --describe tool_name
```

This loads ONLY that tool's schema, not all tools.

## Examples

### Example 1: Get current user

User: "获取我的语雀用户信息"

```bash
cd $SKILL_DIR
python executor.py --call '{"tool": "yuque_get_current_user", "arguments": {}}'
```

### Example 2: Search documents

User: "搜索关于 Python 的文档"

```bash
cd $SKILL_DIR
python executor.py --call '{"tool": "yuque_search", "arguments": {"query": "Python", "type": "doc"}}'
```

### Example 3: Create a document

First, get tool schema:
```bash
cd $SKILL_DIR
python executor.py --describe yuque_create_doc
```

Then create:
```bash
cd $SKILL_DIR
python executor.py --call '{"tool": "yuque_create_doc", "arguments": {"repo_id": "your-repo", "title": "New Doc", "body": "# Content"}}'
```

### Example 4: List all available tools

```bash
cd $SKILL_DIR
python executor.py --list
```

## Error Handling

If the executor returns an error:
- Check the tool name is correct
- Verify required arguments are provided
- Ensure YUQUE_TOKEN is set in mcp-config.json
- Ensure the MCP server is accessible

## Configuration

Edit `mcp-config.json` to set your Yuque API token:

```json
{
  "name": "yuque",
  "command": "uvx",
  "args": ["yuque-sdk"],
  "env": {
    "YUQUE_TOKEN": "your-actual-token-here"
  }
}
```

Get your token from: https://www.yuque.com → Settings → Developer Settings → Personal Access Token

---

*This skill wraps the yuque-sdk MCP server for efficient context usage.*

**GitHub**: https://github.com/jhjgoo/yuque-sdk
