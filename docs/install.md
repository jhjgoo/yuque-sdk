# Yuque SDK — Installation Guide

## For Humans

Copy this to your AI Agent:

```
帮我安装 Yuque SDK MCP：https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/docs/install.md
```

> 🔑 **需要准备**: 语雀 API Token
> 获取方式：登录 https://www.yuque.com → 设置 → 开发者设置 → 创建 Personal Access Token

---

## For AI Agents

### Goal

Install Yuque SDK and configure the MCP server so AI agents can access Yuque documents, repositories, and teams. After installation, users can use 26 MCP tools to interact with Yuque API.

### ⚠️ Boundaries

When fixing issues, stay within these limits:

- **DO NOT** run commands with `sudo` unless the user explicitly approved
- **DO NOT** modify system files outside user's home directory
- **DO NOT** store tokens in plain text files (use environment variables)
- If something requires elevated permissions, **tell the user** what's needed

### 📁 Directory Rules

| Purpose | Location | Example |
|---------|----------|---------|
| Config files | User's MCP client config | `~/.config/cherry-studio/` |
| Cache | UV cache | `~/.cache/uv/` |
| Skills | Claude skills | `~/.claude/skills/yuque-mcp/` |

### Step 1: Check Prerequisites

**Check Python version (requires 3.10+):**

```bash
python3 --version
```

If Python < 3.10, tell the user to upgrade Python first.

**Check UV installation:**

```bash
uv --version
```

If UV is not installed, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Verify Installation

Test that the MCP server works:

```bash
uv cache clean
uvx yuque-sdk --help
```

Expected output should show:
```
usage: yuque-mcp [-h] [--version] [--transport {stdio,sse,http}] ...

Yuque MCP Server - Expose Yuque API to AI assistants via MCP
```

If it shows an error about `yuque-sdk` not found, wait a few minutes for PyPI mirrors to sync, then retry.

### Step 3: Get Yuque API Token

Ask the user for their Yuque API Token. Guide them:

> 请提供你的语雀 API Token：
> 1. 登录 https://www.yuque.com
> 2. 点击右上角头像 → 设置
> 3. 左侧菜单选择「开发者设置」
> 4. 点击「新建」创建 Personal Access Token
> 5. 复制 Token 给我

**Important**: Token should start with a string like `XLt4...` — do NOT share this publicly.

### Step 4: Configure MCP Client

Based on which MCP client the user has, provide the appropriate configuration:

#### For Cherry Studio

Add to MCP settings:

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uvx",
      "args": ["yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "<USER_TOKEN_HERE>"
      }
    }
  }
}
```

#### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uvx",
      "args": ["yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "<USER_TOKEN_HERE>"
      }
    }
  }
}
```

#### For Cursor / Other MCP Clients

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uvx",
      "args": ["yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "<USER_TOKEN_HERE>"
      }
    }
  }
}
```

Replace `<USER_TOKEN_HERE>` with the actual token from Step 3.

### Step 5: Verify MCP Tools

After configuration, ask the user to:

1. **Restart their MCP client** (completely quit and reopen)
2. **Check available tools** — should see 26 Yuque tools:
   - `yuque_get_current_user`
   - `yuque_create_doc`
   - `yuque_search`
   - ... and 23 more

If only 5 tools appear, there may be a package conflict. Use this config instead:

```json
{
  "mcpServers": {
    "yuque": {
      "command": "uvx",
      "args": ["--from", "yuque-sdk", "yuque-sdk"],
      "env": {
        "YUQUE_TOKEN": "<USER_TOKEN_HERE>"
      }
    }
  }
}
```

### Step 6: Test Basic Functions

Run a simple test to verify everything works:

> 请尝试调用 `yuque_get_current_user` 工具来验证连接是否正常

Expected: Returns user information including login name, avatar, etc.

If it fails with authentication error, the token may be invalid or expired.

### 🛠 Troubleshooting

#### "yuque-sdk not found"

```bash
uv cache clean
uvx yuque-sdk --help
```

#### "Only 5 tools showing"

There's another package `yuque_mcp` on PyPI with the same command name. Use `--from`:

```json
"args": ["--from", "yuque-sdk", "yuque-sdk"]
```

#### "Authentication failed"

1. Verify token is correct (no extra spaces)
2. Check token hasn't expired
3. Regenerate token from Yuque settings

#### "Connection closed"

1. Check `YUQUE_TOKEN` is set in the config
2. Restart the MCP client
3. Check network connectivity to yuque.com

### 📋 Available MCP Tools (26 total)

| Category | Tools |
|----------|-------|
| **User** | `yuque_get_current_user`, `yuque_get_user`, `yuque_get_user_groups` |
| **Document** | `yuque_get_doc`, `yuque_create_doc`, `yuque_update_doc`, `yuque_delete_doc`, + 5 more |
| **Repository** | `yuque_get_repo`, `yuque_list_repos`, `yuque_get_repo_toc`, + 3 more |
| **Group** | `yuque_get_group`, `yuque_get_group_repos`, `yuque_get_group_members`, + 2 more |
| **Search** | `yuque_search` |

### ✅ Installation Complete

Once all steps are done, confirm with the user:

> ✅ Yuque SDK MCP 安装完成！
> 
> 你现在可以使用 26 个语雀工具：
> - 获取用户信息
> - 创建/编辑/删除文档
> - 搜索知识库内容
> - 管理团队和仓库
> 
> 试试说：「帮我获取我的语雀用户信息」

---

## Optional: Install Claude Skills

For enhanced Claude Code experience, install the skills:

```bash
mkdir -p ~/.claude/skills
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque-mcp/SKILL.md \
  -o ~/.claude/skills/yuque-mcp/SKILL.md
```

This adds contextual help for MCP tool usage.

---

## Links

- **PyPI**: https://pypi.org/project/yuque-sdk/
- **GitHub**: https://github.com/jhjgoo/yuque-sdk
- **Yuque API Docs**: https://www.yuque.com/yuque/developer
