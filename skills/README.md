# Yuque Skills 安装指南

本文件夹包含 Claude Code (Claude Desktop) 专用技能 (Skills)，用于增强 yuque-python-sdk 项目的开发体验。

## 技能列表

| 技能名称 | 描述 |
|---------|------|
| `yuque-sdk` | yuque SDK 开发技能 - 用于添加新 API、修复 bug、写测试 |
| `yuque-mcp` | yuque MCP 服务器技能 - 用于 MCP 工具测试和调试 |

## 安装方法

### 方法一：全局安装（推荐）

将技能复制到 Claude 的全局技能目录：

```bash
# 创建全局技能目录
mkdir -p ~/.claude/skills

# 复制技能到全局目录
cp -r skills/yuque-sdk ~/.claude/skills/
cp -que-mcp ~/.r skills/yuclaude/skills/
```

**效果**: 这些技能将对你所有 Claude 项目生效。

### 方法二：项目级安装

将技能复制到当前项目：

```bash
# 创建项目技能目录
mkdir -p .claude/skills

# 复制技能到项目目录
cp -r skills/yuque-sdk .claude/skills/
cp -r skills/yuque-mcp .claude/skills/
```

**效果**: 这些技能仅对当前项目生效。

### 方法三：复制到 skills 目录

```bash
# 方案 A: 复制整个 skills 文件夹到全局
cp -r /Users/jianghongjian/Workspace/Code/Python/yuque/skills ~/.claude/skills/yuque

# 方案 B: 符号链接（推荐开发时使用）
ln -sf /Users/jianghongjian/Workspace/Code/Python/yuque/skills/yuque-sdk ~/.claude/skills/yuque-sdk
ln -sf /Users/jianghongjian/Workspace/Code/Python/yuque/skills/yuque-mcp ~/.claude/skills/yuque-mcp
```

**注意**: 使用符号链接可以在修改技能后立即生效，无需重新复制。

## 使用方法

### 手动调用技能

在 Claude 中输入：

```
/yuque-sdk
```

或

```
/yuque-mcp
```

### 自动触发

Claude 会根据对话内容自动选择合适的技能。例如：
- 当你讨论 SDK 代码时会触发 `yuque-sdk`
- 当你测试 MCP 工具时会触发 `yuque-mcp`

## 技能详解

### yuque-sdk

用于 yuque-python-sdk 库开发：

- 添加新的 API 端点
- 修复 bug
- 编写测试
- 扩展功能

包含：
- 项目结构说明
- API 开发模式
- 测试运行方法
- 常用 API 路径

### yuque-mcp

用于 MCP 服务器开发和测试：

- 列出所有可用工具
- 测试工具功能
- 调试工具问题
- API 操作指南

包含：
- 所有 MCP 工具列表
- 测试示例
- 常见问题解决

## 验证安装

安装完成后，可以询问 Claude：

```
What skills do you have available?
```

或直接使用：

```
/yuque-sdk 帮助
```

## 卸载技能

```bash
# 删除全局技能
rm -rf ~/.claude/skills/yuque-sdk
rm -rf ~/.claude/skills/yuque-mcp

# 删除项目技能
rm -rf .claude/skills/yuque-sdk
rm -rf .claude/skills/yuque-mcp
```

## 技能格式

技能遵循 [Agent Skills](https://agentskills.io) 标准：

```yaml
---
name: skill-name
description: 技能描述 - 告诉 Claude 何时使用这个技能
---

# 技能说明文档
```

## 更多信息

- [Claude Skills 官方文档](https://code.claude.com/docs/en/skills)
- [Agent Skills 标准](https://agentskills.io)
- [官方技能示例](https://github.com/anthropics/skills)
