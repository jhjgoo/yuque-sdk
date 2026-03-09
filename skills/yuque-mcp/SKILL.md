---
name: yuque-mcp
description: Development and usage skill for yuque MCP server. Use when working with MCP tools, debugging tool issues, or needing to test yuque API operations.
---

# Yuque MCP Server Guide

This skill helps with MCP server development and testing.

## MCP Tools Available

### User Tools
- `yuque_get_current_user` - Get authenticated user info
- `yuque_get_user` - Get user by ID (deprecated)
- `yuque_get_user_groups` - Get user's groups (deprecated)

### Repository Tools
- `yuque_list_repos` - List all accessible repositories
- `yuque_get_repo` - Get repo by ID
- `yuque_get_repo_by_path` - Get repo by group/login and slug
- `yuque_get_user_repos` - Get repos for specific user
- `yuque_get_group_repos` - Get repos in a group

### TOC Tools
- `yuque_get_repo_toc` - Get table of contents
- `yuque_get_repo_toc_by_path` - Get TOC by path

### Document Tools
- `yuque_get_doc` - Get document by ID
- `yuque_get_docs_by_repo` - List docs in repo
- `yuque_get_docs_by_path` - List docs by path
- `yuque_create_doc` - Create document
- `yuque_create_doc_by_path` - Create document by path
- `yuque_update_doc` - Update document (requires book_id + doc_id)
- `yuque_update_doc_by_repo` - Update document in repo
- `yuque_delete_doc` - Delete document (requires book_id + doc_id)

### Search Tools
- `yuque_search` - Search documents, repos, users, groups

### Group Tools
- `yuque_get_group` - Get group info (deprecated - API not available)
- `yuque_get_group_members` - Get group members
- `yuque_get_group_statistics` - Get group statistics

## Testing MCP Tools

When testing, create temporary documents:

```python
# Create test document
yuque_create_doc_by_path(
    group_login="cfzdbo",
    book_slug="gxbqyx",
    title="Test Document",
    body="# Test"
)

# Update (note: requires book_id)
yuque_update_doc(
    book_id=32715513,
    doc_id=123456,
    title="Updated Title"
)

# Delete (note: requires book_id)
yuque_delete_doc(
    book_id=32715513,
    doc_id=123456
)
```

## MCP Client Configuration

### Recommended: Using `uv run`

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uv",
      "args": ["run", "--with", "yuque-sdk[mcp]", "yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "your-token"
      }
    }
  }
}
```

**Why `uv run` instead of `uvx`?**
- `uvx` does not support Python extras (e.g., `[mcp]`)
- The `[mcp]` extra includes the required `mcp` dependency
- `uv run --with` creates an isolated environment with all dependencies

### Alternative: Development Mode

For local development:

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uv",
      "args": ["--directory", "/path/to/yuque", "run", "yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "your-token"
      }
    }
  }
}
```

### Alternative: Pip Installation

First install: `pip install 'yuque-sdk[mcp]'`

```json
{
  "mcpServers": {
    "yuque": {
      "command": "yuque-sdk",
      "env": {
        "YUQUE_TOKEN": "your-token"
      }
    }
  }
}
```

## Common Issues

1. **404 errors**: Check API endpoint paths - some require book_id
2. **Token issues**: Ensure YUQUE_TOKEN is set correctly
3. **Async issues**: MCP tools must be async functions
