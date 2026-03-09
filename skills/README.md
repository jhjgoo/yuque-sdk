# Yuque Skills

语雀 MCP 服务的 Claude/Qoder Skill 封装，提供高效的上下文管理。

## 为什么用 Skill 而不是直接用 MCP？

| 方式 | 上下文占用 | 适用场景 |
|-----|----------|---------|
| MCP 直连 | ~15k tokens (26 工具全部加载) | 需要频繁调用多个工具 |
| Skill 封装 | ~500 tokens (按需加载) | 偶尔使用，节省上下文 |

## 安装

### 方式 1：一键安装（推荐）

告诉 AI Agent：

```
帮我安装 Yuque Skill：https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/docs/install.md
```

### 方式 2：手动安装

```bash
# Claude Code
mkdir -p ~/.claude/skills
curl -sSL https://github.com/jhjgoo/yuque-sdk/archive/main.tar.gz | \
  tar -xz --strip-components=2 -C ~/.claude/skills yuque-sdk-main/skills/yuque

# Qoder
mkdir -p ~/.qoder/skills
curl -sSL https://github.com/jhjgoo/yuque-sdk/archive/main.tar.gz | \
  tar -xz --strip-components=2 -C ~/.qoder/skills yuque-sdk-main/skills/yuque
```

### 方式 3：克隆仓库

```bash
git clone https://github.com/jhjgoo/yuque-sdk.git ~/.yuque-sdk
ln -sf ~/.yuque-sdk/skills/yuque ~/.claude/skills/yuque
```

## 配置

安装后，编辑 `~/.claude/skills/yuque/mcp-config.json`：

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

Token 获取：https://www.yuque.com → 设置 → 开发者设置 → Personal Access Token

## 使用

在 Claude Code 或 Qoder 中：

```
/yuque
```

加载后即可使用 26 个语雀工具：用户管理、文档管理、仓库管理、团队管理、搜索等。

## 包含的工具

| 类别 | 工具 |
|-----|------|
| 用户 | `yuque_get_current_user`, `yuque_get_user`, `yuque_get_user_groups` |
| 文档 | `yuque_get_doc`, `yuque_create_doc`, `yuque_update_doc`, `yuque_delete_doc`, ... |
| 仓库 | `yuque_get_repo`, `yuque_list_repos`, `yuque_get_repo_toc`, ... |
| 团队 | `yuque_get_group`, `yuque_get_group_repos`, `yuque_get_group_members`, ... |
| 搜索 | `yuque_search` |

## 链接

- **PyPI**: https://pypi.org/project/yuque-sdk/
- **GitHub**: https://github.com/jhjgoo/yuque-sdk
