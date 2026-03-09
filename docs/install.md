# Yuque Skill — Installation Guide

## For Humans

Copy this to your AI Agent:

```
帮我安装 Yuque Skill：https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/docs/install.md
```

---

## For AI Agents

### Goal

Install Yuque Skill for Claude Code / Qoder to enable dynamic access to Yuque API with efficient context management.

### ⚠️ Boundaries

- **DO NOT** run commands with `sudo`
- **DO NOT** modify files outside `~/.claude/` or `~/.qoder/`
- **DO NOT** overwrite existing skills without asking

### Step 1: Detect Agent Type

Check which AI agent the user is using:

**For Claude Code:**
```bash
ls -la ~/.claude/ 2>/dev/null && echo "Claude detected" || echo "Claude not found"
```

**For Qoder:**
```bash
ls -la ~/.qoder/ 2>/dev/null && echo "Qoder detected" || echo "Qoder not found"
```

### Step 2: Install Skill

**For Claude Code:**
```bash
mkdir -p ~/.claude/skills/yuque
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/SKILL.md \
  -o ~/.claude/skills/yuque/SKILL.md
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/executor.py \
  -o ~/.claude/skills/yuque/executor.py
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/mcp-config.json \
  -o ~/.claude/skills/yuque/mcp-config.json
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/package.json \
  -o ~/.claude/skills/yuque/package.json
chmod +x ~/.claude/skills/yuque/executor.py
```

**For Qoder:**
```bash
mkdir -p ~/.qoder/skills/yuque
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/SKILL.md \
  -o ~/.qoder/skills/yuque/SKILL.md
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/executor.py \
  -o ~/.qoder/skills/yuque/executor.py
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/mcp-config.json \
  -o ~/.qoder/skills/yuque/mcp-config.json
curl -sSL https://raw.githubusercontent.com/jhjgoo/yuque-sdk/main/skills/yuque/package.json \
  -o ~/.qoder/skills/yuque/package.json
chmod +x ~/.qoder/skills/yuque/executor.py
```

### Step 3: Get Yuque API Token

Ask the user for their Yuque API Token:

> 请提供你的语雀 API Token：
> 1. 登录 https://www.yuque.com
> 2. 点击右上角头像 → 设置
> 3. 左侧菜单选择「开发者设置」
> 4. 点击「新建」创建 Personal Access Token
> 5. 复制 Token 给我

### Step 4: Configure Token

Once user provides the token, update the config:

**For Claude Code:**
```bash
cat > ~/.claude/skills/yuque/mcp-config.json << 'EOF'
{
  "name": "yuque",
  "command": "uvx",
  "args": ["yuque-sdk"],
  "env": {
    "YUQUE_TOKEN": "USER_TOKEN_HERE"
  }
}
EOF
```

**For Qoder:**
```bash
cat > ~/.qoder/skills/yuque/mcp-config.json << 'EOF'
{
  "name": "yuque",
  "command": "uvx",
  "args": ["yuque-sdk"],
  "env": {
    "YUQUE_TOKEN": "USER_TOKEN_HERE"
  }
}
EOF
```

Replace `USER_TOKEN_HERE` with the actual token from user.

### Step 5: Install Dependencies

```bash
pip install mcp
```

### Step 6: Verify Installation

**Check files exist:**
```bash
ls -la ~/.claude/skills/yuque/
# or
ls -la ~/.qoder/skills/yuque/
```

Expected output should show: `SKILL.md`, `executor.py`, `mcp-config.json`, `package.json`

**Test executor:**
```bash
cd ~/.claude/skills/yuque && python executor.py --list
# or
cd ~/.qoder/skills/yuque && python executor.py --list
```

Expected output: JSON array of 26 available tools.

### 🛠 Troubleshooting

#### "mcp package not installed"

```bash
pip install mcp
```

#### "YUQUE_TOKEN not set"

Check mcp-config.json has the correct token:
```bash
cat ~/.claude/skills/yuque/mcp-config.json
```

#### "uvx: command not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### "Permission denied"

```bash
chmod +x ~/.claude/skills/yuque/executor.py
```

### ✅ Installation Complete

Once done, confirm with the user:

> ✅ Yuque Skill 安装完成！
> 
> 使用方式：在对话中输入 `/yuque` 加载技能
> 
> 可用工具：26 个语雀 API 工具
> - 用户管理：获取用户信息、查看团队
> - 文档管理：创建、编辑、删除、搜索文档
> - 仓库管理：管理知识库
> - 团队管理：管理团队成员
> 
> 试试说：「使用语雀搜索 Python 相关文档」

### 🗑 Uninstall

```bash
rm -rf ~/.claude/skills/yuque
# or
rm -rf ~/.qoder/skills/yuque
```

---

## Links

- **GitHub**: https://github.com/jhjgoo/yuque-sdk
- **PyPI**: https://pypi.org/project/yuque-sdk/
- **Yuque API**: https://www.yuque.com/yuque/developer
