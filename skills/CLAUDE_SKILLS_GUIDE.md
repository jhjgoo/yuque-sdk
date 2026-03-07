# Claude Skills 完全攻略指南

> Claude Code 技能系统完全指南 - 2026年3月更新

## 目录

1. [什么是 Skills](#1-什么是-skills)
2. [Skill 文件格式](#2-skill-文件格式)
3. [YAML Frontmatter 参考](#3-yaml-frontmatter-参考)
4. [变量替换](#4-变量替换)
5. [Hooks 钩子系统](#5-hooks-钩子系统)
6. [内置技能](#6-内置技能)
7. [技能存储位置](#7-技能存储位置)
8. [调用方法](#8-调用方法)
9. [最佳实践](#9-最佳实践)
10. [故障排除](#10-故障排除)
11. [创建示例](#11-创建示例)
12. [安装使用](#12-安装使用)

---

## 1. 什么是 Skills

Skills（技能）是 Claude Code 的可复用指令包，用于扩展 Claude 的能力。遵循 [Agent Skills](https://agentskills.io) 开放标准。

### 核心特性

- **自动触发**: Claude 根据对话上下文自动加载技能
- **手动调用**: 通过 `/skill-name` 命令调用
- **参数支持**: 支持位置参数和动态变量
- **工具限制**: 可限制技能可用工具

---

## 2. Skill 文件格式

### 文件结构

```
skill-name/
├── SKILL.md           # 主指令（必需）
├── template.md        # 模板文件
├── examples/         # 示例输出
│   └── sample.md
├── scripts/          # 辅助脚本
│   └── helper.sh
└── reference.md      # 参考文档
```

### SKILL.md 格式

`SKILL.md` 文件包含两部分：

1. **YAML Frontmatter** - 元数据（`---` 之间）
2. **Markdown Body** - Claude 的指令

---

## 3. YAML Frontmatter 参考

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | 否 | 显示名称（小写字母、数字、连字符，最大64字符） |
| `description` | 推荐 | 技能描述，告诉 Claude 何时使用 |
| `argument-hint` | 否 | 自动完成提示，如 `[issue-number]` |
| `disable-model-invocation` | 否 | `true` = 仅用户可通过 `/name` 调用 |
| `user-invocable` | 否 | `false` = 仅 Claude 可调用 |
| `allowed-tools` | 否 | 技能激活时允许的工具 |
| `model` | 否 | 使用的模型 |
| `context` | 否 | `fork` = 在分支子代理中运行 |
| `agent` | 否 | 子代理类型（Explore, Plan, general-purpose） |
| `hooks` | 否 | 技能生命周期的钩子 |

---

## 4. 变量替换

### 动态变量

| 变量 | 说明 |
|------|------|
| `$ARGUMENTS` | 调用时传递的所有参数 |
| `$ARGUMENTS[N]` | 按索引访问特定参数 |
| `$0`, `$1` | 位置参数的简写形式 |
| `${CLAUDE_SESSION_ID}` | 当前会话 ID |
| `${CLAUDE_SKILL_DIR}` | 技能目录路径 |

### 使用示例

```yaml
---
name: migrate-component
description: Migrate a component between frameworks
---

Migrate the $0 component from $1 to $2.
```

调用: `/migrate-component SearchBar React Vue`

---

## 5. Hooks 钩子系统

### 12个生命周期事件

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 会话开始或恢复 |
| `UserPromptSubmit` | Claude 处理你的提示前 |
| `PreToolUse` | 任何工具执行前（可阻止） |
| `PostToolUse` | 工具成功后 |
| `PostToolUseFailure` | 工具失败后 |
| `PermissionRequest` | 权限对话框出现时 |
| `Stop` | Claude 完成响应 |
| `SubagentStart/Stop` | 子代理生命周期 |
| `PreCompact` | 上下文压缩前 |
| `InstructionsLoaded` | CLAUDE.md/rules 加载时 |

### Hook 配置示例

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate.sh"
          }
        ]
      }
    ]
  }
}
```

### 退出码

| 退出码 | 含义 | Claude 行为 |
|--------|------|------------|
| 0 | 成功 | 解析 JSON 输出 |
| 2 | 阻止错误 | 阻止操作 |
| 其他 | 非阻止错误 | 继续执行 |

---

## 6. 内置技能

| 技能 | 用途 |
|------|------|
| `/simplify` | 审查代码的可复用性、质量、效率问题 |
| `/batch <instruction>` | 编排大规模并行变更 |
| `/debug [description]` | 排查当前会话问题 |
| `/loop [interval] <prompt>` | 按计划运行提示 |
| `/claude-api` | 加载 Claude API 参考文档 |

---

## 7. 技能存储位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 企业级 | 托管设置 | 组织内所有用户 |
| 个人级 | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目 |
| 项目级 | `.claude/skills/<skill-name>/SKILL.md` | 当前项目 |
| 插件级 | `<plugin>/skills/<skill-name>/SKILL.md` | 插件启用范围 |

**优先级**: 企业 > 个人 > 项目 > 插件

---

## 8. 调用方法

### 用户直接调用

```
/skill-name
/skill-name 参数1 参数2
```

### 自动调用

Claude 根据描述自动加载技能。

### 控制调用

| Frontmatter | 用户可调用 | Claude 可调用 |
|-------------|-----------|--------------|
| (默认) | 是 | 是 |
| `disable-model-invocation: true` | 是 | 否 |
| `user-invocable: false` | 否 | 是 |

---

## 9. 最佳实践

### 技能设计模式

#### 1. 参考内容

```yaml
---
name: api-conventions
description: API 设计规范
---

编写 API 端点时:
- 使用 RESTful 命名
- 返回一致的错误格式
```

#### 2. 任务内容

```yaml
---
name: deploy
description: 部署到生产环境
disable-model-invocation: true
context: fork
---

部署应用:
1. 运行测试
2. 构建
3. 推送到部署目标
```

### 工具限制

```yaml
---
name: safe-reader
description: 只读文件不做修改
allowed-tools: Read, Grep
---

探索代码库结构。
不要修改任何文件 - 只读取和分析。
```

### 目录组织

```
my-skill/
├── SKILL.md           # 必需 - 主指令
├── reference.md       # 详细文档（按需加载）
├── examples.md        # 使用示例
└── scripts/
    └── helper.py     # 实用工具脚本
```

---

## 10. 故障排除

### 问题：技能不触发

1. **检查描述** - 包含用户自然会说的关键词
2. **验证技能存在** - 运行 `/help` 列出可用技能
3. **重新表述请求** - 更贴近描述
4. **直接调用** - 如果用户可调用，使用 `/skill-name`

### 问题：技能触发过于频繁

1. **使描述更具体**
2. **添加 `disable-model-invocation: true`**

### 问题：上下文限制

- **当前（2026）**: ~33K tokens 保留用于压缩缓冲（约16.5%）
- **触发点**: ~83.5% 上下文窗口
- **覆盖**: 设置 `CLAUDE_AUTOMPACT_PCT_OVERRIDE` (1-100)

### 问题：模型设置不生效

**已知问题**: `model:` frontmatter 不管理目标模型窗口的上下文
- 完整对话历史仍传递给较小的模型
- 解决方法: 为不同模型使用单独会话

---

## 11. 创建示例

### 示例1：基础技能

```yaml
---
name: explain-code
description: 用视觉图表和类比解释代码。用于解释代码如何工作、教学代码库，或用户问"这是如何工作的"时
---

解释代码时，始终包含:

1. **从类比开始**: 将代码与日常生活中的事物进行比较
2. **画图**: 用 ASCII 艺术展示流程、结构或关系
3. **逐步讲解**: 解释代码逐步发生什么
4. **突出陷阱**: 常见的错误或误解是什么?

保持解释对话式。对于复杂概念，使用多个类比。
```

### 示例2：带参数的任务

```yaml
---
name: fix-issue
description: 修复 GitHub issue
disable-model-invocation: true
---

按照我们的编码标准修复 GitHub issue $ARGUMENTS。

1. 阅读 issue 描述
2. 理解需求
3. 实现修复
4. 编写测试
5. 创建提交
```

### 示例3：带允许工具的限制

```yaml
---
name: safe-reader
description: 只读文件不做修改
allowed-tools: Read, Grep, Glob
---

探索代码库以理解架构。
不要修改任何文件 - 只读取和分析。
```

### 示例4：子代理研究技能

```yaml
---
name: deep-research
description: 彻底研究一个主题
context: fork
agent: Explore
---

彻底研究 $ARGUMENTS:

1. 使用 Glob 和 Grep 查找相关文件
2. 阅读和分析代码
3. 用具体文件引用总结发现
```

---

## 12. 安装使用

### 安装到全局

```bash
# 创建全局技能目录
mkdir -p ~/.claude/skills

# 复制技能到全局目录
cp -r skills/yuque-sdk ~/.claude/skills/
cp -r skills/yuque-mcp ~/.claude/skills/
```

### 安装到项目

```bash
# 创建项目技能目录
mkdir -p .claude/skills

# 复制技能到项目目录
cp -r skills/yuque-sdk .claude/skills/
cp -r skills/yuque-mcp .claude/skills/
```

### 符号链接（推荐开发时使用）

```bash
ln -sf /path/to/yuque/skills/yuque-sdk ~/.claude/skills/yuque-sdk
ln -sf /path/to/yuque/skills/yuque-mcp ~/.claude/skills/yuque-mcp
```

### 使用方法

```
# 直接调用
/yuque-sdk

# 或
/yuque-mcp

# 自动触发
Claude 会根据对话内容自动选择合适的技能
```

---

## 参考资源

- [官方文档](https://code.claude.com/docs/en/skills)
- [Agent Skills 标准](https://agentskills.io)
- [官方技能仓库](https://github.com/anthropics/skills)
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)

---

*本文档最后更新于 2026-03-07*
