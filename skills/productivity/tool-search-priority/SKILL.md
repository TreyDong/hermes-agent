---
name: task-execution-workflow
description: 任务执行标准流程 — 拿到任何任务时，先查此清单决定用什么工具。包含所有已安装 CLI（gh/twitter/xhs/bili/discord-cli/lark-cli/opencli/ddgs/google）和完整优先级：CLI优先 → Skill → MCP内置 → find-skill → 浏览器。
trigger: 所有任务开始前必读。这不是"搜索工具"的skill，而是所有工作的第一步。
---

# 任务执行标准流程

## 重要提示

> **这是一个必读清单，不是工具索引。**
> 名称里的"tool"指的是"完成任务所用的手段"，不是"搜索工具"。

## 触发条件（任何任务开始前都必须检查）

- 拿到任何任务的第一步
- 不确定该怎么干的时候
- 习惯性地想用浏览器之前
- 想找有没有现成skill的时候

---

## 优先级概览

| 优先级 | 类别 | 说明 |
|--------|------|------|
| **P0** | CLI / 原生命令 | 直接调用已安装的程序，最快最可靠 |
| **P1** | Skill 工具 | 检查现有 skill 是否已封装该能力 |
| **P2** | MCP / 内置工具 | 当前会话内可直接调用的工具 |
| **P3** | find-skill 搜索 | 前两级都不满足时查找合适的 skill |
| **P4** | 浏览器 / 搜索引擎 | 最后手段，仅在以上都无效时使用 |

---

## P0 — CLI / 原生命令（最高优先级）

**本机已安装的所有 CLI 工具，按用途分类：**

### 社交媒体 & 消息平台

| 平台 | 命令 | 路径 | 能力 |
|------|------|------|------|
| **Twitter/X** | `twitter` | pip | 发推、读推、搜索、timeline、书签 |
| **小红书** | `xhs` | pip | 发笔记、评论、点赞、收藏 |
| **哔哩哔哩** | `bili` | pip | 下载音视频、投币、点赞、动态 |
| **Discord** | `discord-cli`, `discocli`, `discordctl` | ~/bin/ | 消息、频道、thread、搜索 |
| **飞书** | `lark-cli` | npm global | 文档、表格、审批、日历、联系人 |
| **微信** | `md2wechat` | pip | Markdown 转微信公众号 HTML |
| **Telegram** | ❌ 需通过 gateway 配置 | — | 消息收发 |

### 网络搜索

| 命令 | 路径 | 用途 |
|------|------|------|
| **`ddgs`** | pip | DuckDuckGo 命令行搜索 |
| **`google`** | pip | Google 命令行搜索 |
| **`curl`** | 系统 | HTTP 请求、API 调试 |

### Git / 代码

| 命令 | 用途 |
|------|------|
| **`gh`** | GitHub CLI（PR/Issue/Release/搜索/代码审查） |
| **`git`** | 版本控制 |
| **`hf`** | HuggingFace Hub（模型/数据集搜索下载） |

### 文件 & 内容搜索

| 命令 | 用途 |
|------|------|
| **`rg`** (ripgrep) | 文件内容搜索（最快） |
| **`fd`** / **`fzf`** | 文件名搜索 |
| **`find`** / **`ls`** | 文件列表 |

### 数据处理

| 命令 | 用途 |
|------|------|
| **`jq`** | JSON 处理 |
| **`yq`** | YAML 处理 |
| **`python3`** | 脚本、数据处理、API 调用 |

### 浏览器自动化

> **opencli** — 有真实登录态的浏览器自动化，优先级高于浏览器。
>
> - 路径：`~/.npm-global/bin/opencli`
> - 用法：`opencli operate <自然语言指令>`
> - 场景：需要登录的网站、复杂交互、验证码

### 其他常用

| 命令 | 用途 |
|------|------|
| `docker` / `docker compose` | 容器管理 |
| `tar` / `zip` / `gzip` | 压缩/解压 |
| `ps` / `top` / `du` / `df` | 系统进程/资源 |
| `base64` / `md5sum` / `openssl` | 编码/哈希 |
| `tmux` / `timeout` / `kill` | 会话/进程管理 |

---

## P1 — Skill 工具

检查现有 skill 是否已封装该能力：

```
mcp_skills_list → skill_view(name) → 加载使用
```

**常见 skill 速查：**

| 场景 | Skill |
|------|-------|
| 查 GitHub PR/Issue | `github` skill |
| 发推特 | `twitter-cli` skill |
| 飞书文档/表格 | `lark-doc`, `lark-sheets`, `lark-base` |
| 飞书审批 | `lark-approval` |
| 飞书日历 | `lark-calendar` |
| 微信发布 | `baoyu-post-to-wechat`, `md2wechat` |
| 视频生成 | `volcengine-seedance-video` |
| 浏览器自动化 | `agent-browser` |
| 执行计划 | `executing-plans` |
| 头脑风暴 | `brainstorming` |
| 内容策略 | `content-strategy` |
| 技能创建 | `skill-creator` |
| 笔记管理 | `obsidian` |
| YouTube | `youtube-summarizer` |
| 网络研究（结构化精准） | `tavily-search` skill（tavily-python 包） |

---

## P2 — MCP / 内置工具

当前会话内可直接调用（无需安装）：**

| 工具 | 用途 |
|------|------|
| `mcp_search_files` | 文件内容搜索 |
| `mcp_read_file` | 读取文件 |
| `mcp_write_file` | 写入文件 |
| `mcp_patch` | 精确文本替换 |
| `mcp_terminal` | 执行任何 shell 命令 |
| `session_search` | 跨会话记忆搜索 |
| `hindsight_recall` / `hindsight_reflect` | 长期记忆检索 |
| `mcp_skills_list` | 列出所有 skill |
| `skill_view(name)` | 加载 skill 详情 |
| `mcp_image_generate` | 图片生成 |
| `mcp_text_to_speech` | 文字转语音 |
| `mcp_mcp_MiniMax_web_search` | MiniMax 网络搜索 |
| `mcp_mcp_MiniMax_understand_image` | 图片理解 |

---

## P3 — find-skill 搜索

前两级都不满足时：

```
描述你的需求 → find-skills → 系统推荐合适的 skill
```

---

## P4 — 浏览器 / 搜索引擎（最后手段）

P0~P3 都无效时才用：

| 工具 | 用途 |
|------|------|
| `web_search` (MiniMax 内置) | 快速搜索，信息可能不如 tavily 准 |
| `browser_navigate` | 需要页面交互/截图/验证码时 |

---

## 决策流程图

```
拿到任务
  │
  ├─ 发推/读推         → `twitter` CLI
  ├─ 小红书操作        → `xhs` CLI
  ├─ 哔哩操作          → `bili` CLI
  ├─ Discord操作       → `discord-cli` / `discocli`
  ├─ GitHub           → `gh` CLI / `github` skill
  ├─ 飞书操作          → `lark-*` skill 系列
  ├─ 文件内容搜索       → `rg` / `mcp_search_files`
  ├─ 网络搜索           → `ddgs` / `google` / `tavily-search` skill
  ├─ Web API请求       → `curl`
  ├─ 记忆/会话         → `session_search` / `hindsight_recall`
  ├─ 需要登录的网页     → `opencli operate`
  ├─ 某个skill         → `mcp_skills_list` → `skill_view`
  │
  └─ 都不行？
       ├─ find-skills 描述需求
       └─ `web_search` / `browser_navigate`
```

---

## 快速判断法则

| 场景 | 首选工具 |
|------|----------|
| 发推/读推 | `twitter` CLI |
| 小红书操作 | `xhs` CLI |
| 哔哩操作 | `bili` CLI |
| Discord操作 | `discord-cli` / `discocli` |
| 查 GitHub PR/Issue | `gh` CLI |
| 飞书文档/表格/审批 | `lark-*` skill |
| 网络搜索（结构化） | `tavily-search` skill / `ddgs` / `google` |
| 网络搜索（简单） | `ddgs` / `google` |
| 搜文件/代码 | `rg` / `mcp_search_files` |
| 搜记忆/会话 | `session_search` / `hindsight_recall` |
| 需要登录态的网页 | `opencli operate` |
| 搜 skill | `mcp_skills_list` + `skill_view` |
| 都不是 | `find-skills` |
| 需要交互/截图/验证码 | `browser_navigate` |

---

## 核心原则

> **能命令行搞定的绝不打开浏览器。**
> 浏览器是最后手段，不是默认选项。
