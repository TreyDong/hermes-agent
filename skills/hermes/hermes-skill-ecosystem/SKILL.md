---
name: hermes-skill-ecosystem
description: Hermes skill 生态管理——安装、查询、安全扫描机制及官方 skill 精选推荐
triggers:
  - hermes skill 安装
  - hermes skill 生态
  - hermes skills list
  - 装哪个 skill 好
---

# Hermes Skill 生态管理

## 存储结构

```
~/.hermes/hermes-agent/skills/           ← 内置 74 个（直接可用）
~/.hermes/hermes-agent/optional-skills/  ← 可选 skill（需单独安装）
```

## 核心 CLI 命令

```bash
hermes skills list              # 列出已安装
hermes skills browse            # 浏览 Hub 全部可用 skill
hermes skills search QUERY      # 搜索 Hub
hermes skills inspect ID        # 安装前预览
hermes skills install ID        # 安装
hermes skills check             # 检查更新
hermes skills update            # 更新过时 skill
hermes skills uninstall NAME    # 卸载
```

## 安装命令格式

```bash
# 官方 Hub
hermes skills install IDENTIFIER

# GitHub 第三方仓库
hermes skills install GITHUB_REPO

# 绕过安全警告（谨慎使用）
hermes skills install IDENTIFIER --force
```

## 安全扫描机制

部分 skill 会被安全扫描拦截，常见原因：
- **路径 traversal**：文件名含 `..`
- **Privilege escalation**：install script 有提权操作
- **CRITICAL 标记**：持久化 + 数据外泄风险

被拦截的 skill 仍可通过 `--force` 强制安装（需用户手动确认）。

## 已安装 skill（2026-04-02）

- `writing-plans`
- `executing-plans`
- `brainstorming`
- `copywriting`
- `content-strategy`
- `systematic-debugging`
- `remotion-best-practices`
- `youtube-summarizer`

## Skill 文件格式

每个 skill 是 `SKILL.md`，YAML frontmatter + Markdown 正文：

```yaml
---
name: example-skill
description: 简短描述
platforms: [macos, linux]
metadata:
  hermes:
    tags: [tag1, tag2]
prerequisites:
  commands: [cmd1]
---

# 正文...
```
