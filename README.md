# Yuque Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/yuque.svg)](https://pypi.org/project/yuque/)
[![Python Versions](https://img.shields.io/pypi/pythonversions/yuque.svg)](https://pypi.org/project/yuque/)
[![License](https://img.shields.io/pypi/l/yuque.svg)](https://opensource.org/licenses/Apache-2.0)

A modern, type-safe Python client library for the [Yuque OpenAPI](https://www.yuque.com/yuque/developer/api).

## Features

- **Modern Python**: Built with Python 3.10+ type hints and Pydantic v2
- **Async/Sync Support**: Both synchronous and asynchronous interfaces
- **Comprehensive Coverage**: Full support for all Yuque API endpoints
- **Type Safety**: Full type annotations with Pydantic models
- **Error Handling**: Detailed exception hierarchy for API errors
- **Pagination**: Automatic pagination handling for list endpoints
- **Smart Caching**: Built-in caching with Redis and memory backends, TTL policies
- **Dual Access**: Access resources by ID or by path (group/book/slug)

## Installation

```bash
# Using uv (recommended)
uv add yuque

# Using pip
pip install yuque
```

### MCP Server Support

To use this library as an MCP (Model Context Protocol) server, install with MCP extras:

```bash
# Using uv
uv add yuque[mcp]

# Using pip
pip install yuque[mcp]
```

This will install additional dependencies:
- `mcp>=0.9.0` - MCP Python SDK for building servers
- `fastapi>=0.100.0` - FastAPI framework (optional, for HTTP transport)
- `uvicorn>=0.22.0` - ASGI server (optional, for HTTP transport)

## 🤖 MCP Server Usage

This library can be used as an **MCP (Model Context Protocol) server**, allowing AI assistants like Claude Desktop to interact with Yuque directly.

### What is MCP?

MCP (Model Context Protocol) is a protocol that enables AI assistants to interact with external tools and services. By running this library as an MCP server, you can:

- ✨ Let Claude Desktop access your Yuque documents and repositories
- 🔍 Search and retrieve Yuque content through natural language
- ✏️ Create and update documents via AI assistance
- 👥 Manage groups and team members
- 📊 Access comprehensive Yuque statistics

### Installation

Install with MCP support:

```bash
# Using uv
uv add yuque[mcp]

# Using pip
pip install yuque[mcp]
```

This installs additional dependencies:
- `mcp>=0.9.0` - MCP Python SDK
- `fastapi>=0.100.0` - FastAPI framework (optional, for HTTP transport)
- `uvicorn>=0.22.0` - ASGI server (optional, for HTTP transport)

### Configuration

Set your Yuque API token as an environment variable:

```bash
# macOS/Linux
export YUQUE_TOKEN='your-api-token-here'

# Windows (Command Prompt)
set YUQUE_TOKEN=your-api-token-here

# Windows (PowerShell)
$env:YUQUE_TOKEN='your-api-token-here'
```

To get your API token:
1. Log in to [Yuque](https://www.yuque.com)
2. Go to **Settings → Developer Settings**
3. Create a new **Personal Access Token**
4. Copy and save the token securely

### Usage Methods

#### 1️⃣ MCP Client Integration (Claude Desktop / Cherry Studio)

Add the MCP server to your MCP client configuration:

**Claude Desktop macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Claude Desktop Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Cherry Studio**: Check your MCP settings for the configuration file location

**Option A: Using `uvx` (Simplest)** ✅

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uvx",
      "args": ["yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Note**: As of v0.1.4+, `mcp` is included in the base dependencies, so `uvx yuque-sdk` works directly.

**Option B: Using `uv run`**

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uv",
      "args": ["run", "--with", "yuque-sdk[mcp]", "yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Why `uv run` instead of `uvx`?**
- `uvx` does **not** support Python extras (e.g., `[mcp]`)
- `yuque-sdk[mcp]` includes required `mcp` dependency
- `uv run --with` properly installs all dependencies in an isolated environment

**Option B: Using `uv run`**

Alternative isolated environment approach:

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uv",
      "args": ["run", "--with", "yuque-sdk", "yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Option C: Using pip installation**

First install with MCP support:
```bash
pip install 'yuque-sdk[mcp]'
```

Then configure:
```json
{
  "mcpServers": {
    "yuque": {
      "command": "yuque-sdk",
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Option C: Using pip installation**

Install globally, then use directly:
```bash
pip install yuque-sdk
```

Then configure:
```json
{
  "mcpServers": {
    "yuque": {
      "command": "yuque-sdk",
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

**Option D: Using specific Python path**

```json
{
  "mcpServers": {
    "yuque": {
      "command": "/usr/bin/python3",
      "args": ["-m", "yuque.mcp.cli"],
      "env": {
        "YUQUE_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

After updating the config:
1. **Restart your MCP client** completely (e.g., Claude Desktop / Cherry Studio)
2. The Yuque tools will appear in the available tools list
3. Start using natural language to interact with Yuque!

**Example prompts:**
- "Search for documents about API design in my Yuque"
- "Get the table of contents for my team's documentation repository"
- "Create a new document titled 'Meeting Notes' in the Engineering knowledge base"
- "Show me all the repositories in my team group"

#### 2️⃣ Command Line Usage

Run the MCP server directly from command line:

```bash
# Start with STDIO transport (default, for MCP clients)
yuque-sdk

# Start with SSE transport (for HTTP-based clients)
yuque-sdk --transport sse

# Start with SSE on custom port
yuque-sdk --transport sse --port 9000

# Start with HTTP transport
yuque-sdk --transport http

# Start with custom host and port
yuque-sdk --transport http --host 127.0.0.1 --port 8888

# Enable debug mode
yuque-sdk --debug

# Set custom log level
yuque-sdk --log-level DEBUG

# Custom server name
yuque-sdk --name "my-yuque-server"
```

**Note**: SSE and HTTP transports require additional dependencies:

```bash
# Install with HTTP support
pip install 'yuque-sdk[mcp]'

# The [mcp] extras includes:
# - fastapi>=0.100.0 (for HTTP server)
# - uvicorn>=0.22.0 (ASGI server)
```

**When to use different transports:**
- **stdio** (default): For Claude Desktop, Cherry Studio local integration
- **sse/http**: For remote server deployment, web-based clients

#### 3️⃣ Programmatic Usage

Use the MCP server in your Python applications:

```python
import asyncio
from yuque.mcp import MCPServer

async def main():
    # Initialize the server
    server = MCPServer(
        token="your-api-token",  # Or use YUQUE_TOKEN env var
        name="my-yuque-server",
        debug=False,
        log_level="INFO"
    )

    # Run the server
    await server.start_async(transport="stdio")

# Run the server
asyncio.run(main())
```

Or use it as a context manager:

```python
from yuque.mcp import MCPServer

async def run_server():
    async with MCPServer(token="your-token") as server:
        # Server is running
        await server.start_async()
```

### 🛠️ Available Tools

The MCP server provides **27 comprehensive tools** for interacting with Yuque:

#### 👤 User Tools (3)
| Tool | Description |
|------|-------------|
| `yuque_get_current_user` | Get current authenticated user's information |
| `yuque_get_user` | Get a specific user by ID |
| `yuque_get_user_groups` | Get groups/teams a user belongs to |

#### 📄 Document Tools (9)
| Tool | Description |
|------|-------------|
| `yuque_get_doc` | Get document by ID |
| `yuque_get_docs_by_repo` | List documents in a repository |
| `yuque_get_docs_by_path` | List documents by group/book path |
| `yuque_create_doc` | Create a new document |
| `yuque_create_doc_by_path` | Create document by path |
| `yuque_update_doc` | Update an existing document |
| `yuque_update_doc_by_repo` | Update document in repository |
| `yuque_delete_doc` | Delete a document |
| `yuque_get_doc_version` | Get a specific document version |

#### 📚 Repository Tools (7)
| Tool | Description |
|------|-------------|
| `yuque_get_repo` | Get repository by ID |
| `yuque_get_repo_by_path` | Get repository by path |
| `yuque_list_repos` | List all accessible repositories |
| `yuque_get_user_repos` | Get user's repositories |
| `yuque_get_group_repos` | Get group's repositories |
| `yuque_get_repo_toc` | Get table of contents |
| `yuque_get_repo_toc_by_path` | Get TOC by path |

#### 👥 Group Tools (7)
| Tool | Description |
|------|-------------|
| `yuque_get_group` | Get group information |
| `yuque_get_group_repos` | Get repositories in a group |
| `yuque_get_group_members` | Get group members |
| `yuque_add_group_member` | Add member to group |
| `yuque_update_group_member` | Update member role |
| `yuque_remove_group_member` | Remove member from group |
| `yuque_get_group_statistics` | Get group statistics |

#### 🔍 Search Tools (1)
| Tool | Description |
|------|-------------|
| `yuque_search` | Search across Yuque (docs, repos, users, groups) |

### 💡 Examples

#### Searching for Documents

```python
# In Claude Desktop, simply ask:
"Search for documents about Python in my Yuque workspace"

# The tool will be called with:
yuque_search(keyword="Python", type="doc", page=1)
```

#### Creating a Document

```python
# Natural language request to Claude:
"Create a new document titled 'API Guide' in the engineering/api-docs repository with markdown content"

# Results in:
yuque_create_doc_by_path(
    group_login="engineering",
    book_slug="api-docs",
    title="API Guide",
    body="# API Guide\n\nWelcome to the API documentation...",
    format="markdown"
)
```

#### Managing Team Members

```python
# Request:
"Add user with ID 12345 to the 'engineering' team as a member"

# Tool call:
yuque_add_group_member(
    login="engineering",
    user_id=12345,
    role=1  # 0=Admin, 1=Member, 2=Read-only
)
```

### 🔧 Troubleshooting

#### Common Issues

**❌ "YUQUE_TOKEN environment variable is required"**

Solution: Make sure you've set the environment variable:
```bash
export YUQUE_TOKEN='your-token-here'
```

**❌ "Authentication failed"**

Possible causes:
- Invalid or expired API token
- Token lacks necessary permissions
- Network connectivity issues

Solution: Generate a new token from Yuque settings and ensure it has the required permissions.

**❌ "Claude Desktop doesn't see the tools"**

Solutions:
1. Verify the config file location is correct
2. Restart Claude Desktop completely (not just refresh)
3. Check the JSON syntax in the config file
4. Ensure `yuque-sdk` is in your PATH or use full path

**❌ "Permission denied"**

Cause: Your token doesn't have access to the resource.

Solution: Check that:
- You have access to the group/repository
- Your token has appropriate scopes
- You're not trying to access private content without permission

**❌ "Rate limit exceeded"**

Solution: Yuque API has rate limits. Wait a moment and try again.

#### Debug Mode

Enable debug mode for verbose logging:

```bash
# Command line
yuque-sdk --debug

# Or in Claude Desktop config
{
  "mcpServers": {
    "yuque": {
      "command": "yuque-sdk",
      "args": ["--debug"],
      "env": {
        "YUQUE_TOKEN": "your-token"
      }
    }
  }
}
```

#### Getting Help

If you encounter issues:

1. **Check the logs**: Debug mode shows detailed error messages
2. **Verify token permissions**: Ensure your token has the necessary scopes
3. **Test the CLI**: Run `yuque-sdk --debug` to see if the server starts correctly
4. **Open an issue**: [GitHub Issues](https://github.com/jhjgoo/yuque-sdk/issues)

### 📚 Best Practices

1. **Token Security**
   - Never commit tokens to version control
   - Use environment variables or secure secret management
   - Rotate tokens periodically

2. **Error Handling**
   - Always check the `success` field in responses
   - Handle rate limits gracefully with retries
   - Validate user inputs before creating/updating content

3. **Performance**
   - Use pagination for large result sets
   - Cache frequently accessed data
   - Limit concurrent requests to avoid rate limiting

4. **Content Management**
   - Use meaningful document titles and slugs
   - Organize content with clear hierarchy
   - Set appropriate visibility levels (public/private)

---

## 🧠 AI Agent Skill (Claude Code / Qoder / OpenClaw)

This library also provides a **Skill** for AI coding assistants, enabling dynamic access to Yuque MCP with efficient context management.

### Why Skill vs MCP?

| Approach | Context Usage | Best For |
|----------|--------------|----------|
| MCP Direct | ~15k tokens (all 26 tools loaded) | Frequent multi-tool usage |
| Skill Wrapper | ~500 tokens (on-demand loading) | Occasional usage, context saving |

### One-Click Installation

Tell your AI Agent:

```
帮我安装 Yuque Skill：https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/docs/install.md
```

The AI will automatically install the skill to the appropriate directory.

### Manual Installation

```bash
# Claude Code
mkdir -p ~/.claude/skills/yuque
curl -sSL https://github.com/jhjgoo/yuque-sdk/archive/main.tar.gz | \
  tar -xz --strip-components=2 -C ~/.claude/skills yuque-sdk-main/skills/yuque

# Qoder
mkdir -p ~/.qoder/skills/yuque
curl -sSL https://github.com/jhjgoo/yuque-sdk/archive/main.tar.gz | \
  tar -xz --strip-components=2 -C ~/.qoder/skills yuque-sdk-main/skills/yuque

# OpenClaw
mkdir -p ~/.openclaw/skills/yuque
curl -sSL https://github.com/jhjgoo/yuque-sdk/archive/main.tar.gz | \
  tar -xz --strip-components=2 -C ~/.openclaw/skills yuque-sdk-main/skills/yuque
```

### Configuration

Edit `mcp-config.json` in the skill directory:

```json
{
  "name": "yuque",
  "command": "uvx",
  "args": ["yuque-sdk"],
  "env": {
    "YUQUE_TOKEN": "your-token-here"
  }
}
```

For OpenClaw, you can also configure via `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "yuque": {
        "enabled": true,
        "apiKey": "your-token-here"
      }
    }
  }
}
```

### Usage

In your AI agent, type:

```
/yuque
```

This loads the skill with access to all 26 Yuque tools.

---

## Quick Start

### Synchronous Usage

```python
from yuque import YuqueClient

# Initialize the client with your API token
client = YuqueClient(token="your-api-token")

# Get current user
user = client.user.get_me()
print(f"Hello, {user.name}!")

# List your repositories
repos = client.repo.list()
for repo in repos:
    print(f"- {repo['name']} ({repo['slug']})")

# Get a specific document
doc = client.doc.get(doc_id=12345)
print(f"Document: {doc['title']}")
```

### Asynchronous Usage

```python
import asyncio
from yuque import YuqueClient

async def main():
    async with YuqueClient(token="your-api-token") as client:
        # Get current user
        user = await client.user.get_me_async()
        print(f"Hello, {user.name}!")

        # List repositories
        repos = await client.repo.list_async()
        for repo in repos:
            print(f"- {repo.name}")

asyncio.run(main())
```

### Using as Context Manager

```python
from yuque import YuqueClient

# Synchronous context manager
with YuqueClient(token="your-token") as client:
    user = client.user.get_me()
    print(user.name)

# Asynchronous context manager
import asyncio
async def async_example():
    async with YuqueClient(token="your-token") as client:
        user = await client.user.get_me_async()
        print(user.name)

asyncio.run(async_example())
```

## API Reference

### User API

```python
# Get current authenticated user
user = client.user.get_me()

# Get user by ID
user = client.user.get_by_id(user_id=123)

# Get groups for a user
groups = client.user.get_groups(user_id=123)
```

### Group API

```python
# Get group by login
group = client.group.get(login="my-group")

# Get group by ID (dual access)
group = client.group.get_by_id(group_id=12345)

# List repositories in a group
repos = client.group.get_repos(login="my-group")

# List group members
members = client.group.get_members(login="my-group")

# Add a member to group
client.group.add_member(login="my-group", user_id=123, role=1)

# Update member role
client.group.update_member(login="my-group", user_id=123, role=0)

# Remove a member
client.group.remove_member(login="my-group", user_id=123)

# Get group statistics
stats = client.group.get_statistics(login="my-group")

# Get member statistics with time range filter
member_stats = client.group.get_member_stats(
    login="my-group",
    range="30d",  # "7d", "30d", "90d"
    page=1,
    limit=20,
)

# Get book statistics
book_stats = client.group.get_book_stats(
    login="my-group",
    range="30d",
)

# Get document statistics
doc_stats = client.group.get_doc_stats(
    login="my-group",
    range="30d",
)
```

### Repository (Book) API

```python
# Get repository by ID
repo = client.repo.get(book_id=123)

# Get repository by path (dual access)
repo = client.repo.get_by_path(group_login="my-group", book_slug="my-repo")

# List all repositories for authenticated user
repos = client.repo.list()

# List user's repositories
repos = client.repo.get_user_repos(login="username")

# List group's repositories
repos = client.repo.get_group_repos(login="my-group")

# Get table of contents
toc = client.repo.get_toc(book_id=123)
toc = client.repo.get_toc_by_path(group_login="my-group", book_slug="my-repo")

# Create a new repository (knowledge base)
repo = client.repo.create_repo(
    owner_login="my-group",
    owner_type="Group",  # or "User"
    name="New Knowledge Base",
    slug="new-kb",
    description="Description here",
    public=0,  # 0=private, 1=public, 2=public to internet
)

# Update an existing repository
repo = client.repo.update_repo(
    book_id=123,
    name="Updated Name",
    description="New description",
    public=1,
)

# Delete a repository
result = client.repo.delete_repo(book_id=123)
```

### Document API

```python
# Get document by ID
doc = client.doc.get(doc_id=12345)

# Get document by path (dual access)
doc = client.doc.get_doc_by_path(
    namespace="my-group/my-book",  # group_login/book_slug
    slug="intro",
    raw=False,  # True for raw markdown
)

# List documents in a repository
docs = client.doc.get_by_repo(book_id=123)

# List documents by path
docs = client.doc.get_by_path(group_login="my-group", book_slug="my-repo")

# Create a document
doc = client.doc.create(
    book_id=123,
    title="My New Document",
    body="# Hello World\n\nThis is my new document.",
    format="markdown",
)

# Create document by path
doc = client.doc.create_by_path(
    group_login="my-group",
    book_slug="my-repo",
    title="New Doc",
    body="Content...",
)

# Update a document by ID
doc = client.doc.update(
    doc_id=12345,
    title="Updated Title",
    body="Updated content...",
)

# Update document by path (dual access)
doc = client.doc.update_by_path(
    namespace="my-group/my-book",
    slug="intro",
    title="Updated Title",
    body="New content",
)

# Delete a document by ID
client.doc.delete(doc_id=12345)

# Delete document by path (dual access)
client.doc.delete_by_path(namespace="my-group/my-book", slug="old-doc")

# Get document version
version = client.doc.get_version(version_id=1)
```

### Search API

```python
# Search across Yuque
results = client.search.search(keyword="python", type="doc")
for result in results:
    print(f"- {result.title}: {result.url}")
```

## Error Handling

The library provides detailed exceptions for different API error scenarios:

```python
from yuque import YuqueClient
from yuque.exceptions import (
    YuqueError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    InvalidArgumentError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
)

try:
    client = YuqueClient(token="your-token")
    user = client.user.get_me()
except AuthenticationError:
    print("Invalid API token")
except PermissionDeniedError:
    print("You don't have permission")
except NotFoundError:
    print("Resource not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except YuqueError as e:
    print(f"API error: {e}")
```

## Configuration

```python
from yuque import YuqueClient

# Custom timeout
client = YuqueClient(token="your-token", timeout=60.0)

# Custom max retries
client = YuqueClient(token="your-token", max_retries=5)
```

## Caching

The SDK provides built-in caching support with multiple backends and automatic TTL policies.

### Basic Usage

```python
from yuque import YuqueClient
from yuque.cache import CacheManager

# Create a cache manager with default memory backend
cache = CacheManager(enabled=True)

# Pass to client
with YuqueClient(token="your-token", cache=cache) as client:
    # First call fetches from API
    user = client.user.get_me()
    
    # Second call returns cached data (faster!)
    user = client.user.get_me()
    
    # Check cache statistics
    stats = cache.stats
    print(f"Hits: {stats.hits}, Misses: {stats.misses}")
```

### Cache Backends

#### Memory Backend (Default)

```python
from yuque.cache import CacheManager, MemoryCacheBackend

# Memory backend - good for single-process applications
backend = MemoryCacheBackend(max_size=1000)
cache = CacheManager(backend=backend, enabled=True)
```

#### Redis Backend (Distributed)

```python
from yuque.cache import AsyncCacheManager, RedisCacheBackend

# Redis backend - good for distributed applications
redis_backend = RedisCacheBackend(
    url="redis://localhost:6379/0",
    key_prefix="yuque:"
)
cache = AsyncCacheManager(backend=redis_backend, enabled=True)

# Use with async client
async with YuqueClient(token="your-token", cache=cache) as client:
    user = await client.user.get_me_async()
```

> **Note**: Redis backend requires `redis` package: `pip install redis`

### TTL Policies

Default TTL (time-to-live) policies:

| Endpoint Pattern | TTL |
|-----------------|-----|
| `/user` | 24 hours |
| `/repos` | 12 hours |
| `/repos/*/docs` | 6 hours |
| `/docs/` | 3 hours |
| `/search` | 1 hour |
| `/groups` | 12 hours |

Customize TTL policies:

```python
from yuque.cache import CacheManager, TTL_POLICIES

custom_policies = {
    **TTL_POLICIES,
    "/docs/": 60 * 60,  # 1 hour for documents
    "/search": 30 * 60,  # 30 minutes for search
}

cache = CacheManager(ttl_policies=custom_policies, default_ttl=1800)
```

### Cache Statistics

```python
# Get cache statistics
stats = cache.stats
print(f"Hit rate: {stats.hit_rate:.2%}")
print(f"Total requests: {stats.total_requests}")
print(f"Avg hit latency: {stats.avg_hit_latency_ms:.2f}ms")

# Get detailed stats as dictionary
stats_dict = cache.get_stats_dict()
print(stats_dict)

# Reset statistics
cache.reset_stats()
```

### Disable Caching

```python
# Disable cache temporarily
cache.enabled = False

# Or create client without cache
client = YuqueClient(token="your-token")  # No caching

# Clear all cached data
cache.clear()
```

## Migration Guide

### Upgrading from v1.x to v2.x

Version 2.0 introduces caching, dual access patterns, and new APIs. Here's how to migrate:

#### New Features (Optional)

**Caching** - Enable for better performance:

```python
# Before (v1.x)
client = YuqueClient(token="your-token")

# After (v2.x) - with caching
from yuque.cache import CacheManager
cache = CacheManager(enabled=True)
client = YuqueClient(token="your-token", cache=cache)
```

**Dual Access** - Access resources by path:

```python
# Before (v1.x) - only by ID
doc = client.doc.get(doc_id=12345)

# After (v2.x) - also by path
doc = client.doc.get_doc_by_path("my-group/my-book", "intro")
```

#### New Repository APIs

```python
# Create repository
repo = client.repo.create_repo(
    owner_login="my-group",
    owner_type="Group",
    name="New KB",
)

# Update repository
client.repo.update_repo(book_id=123, name="Updated Name")

# Delete repository
client.repo.delete_repo(book_id=123)
```

#### New Group Statistics APIs

```python
# Member statistics
stats = client.group.get_member_stats("my-group", range="30d")

# Book statistics
stats = client.group.get_book_stats("my-group", range="30d")

# Document statistics
stats = client.group.get_doc_stats("my-group", range="30d")
```

#### Async Methods

All new methods have async equivalents:

```python
# Sync
repo = client.repo.create_repo(...)

# Async
repo = await client.repo.create_repo_async(...)
```

### Breaking Changes

None. All v1.x APIs remain fully compatible with v2.x.

## Getting Your API Token

1. Log in to [Yuque](https://www.yuque.com)
2. Go to [Developer Settings](https://www.yuque.com/yuque/developer/api)
3. Create a new Personal Access Token
4. Copy the token and use it in your application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Links

- [Yuque OpenAPI Documentation](https://www.yuque.com/yuque/developer/api)
- [PyPI Package](https://pypi.org/project/yuque-sdk/)
- [GitHub Repository](https://github.com/jhjgoo/yuque-sdk)
- [Skill Installation Guide](https://github.com/jhjgoo/yuque-sdk/blob/main/docs/install.md)
