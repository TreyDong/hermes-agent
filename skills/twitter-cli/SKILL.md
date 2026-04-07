---
name: twitter-cli
description: Twitter/X CLI 工具箱 — 发推、读取、搜索、管理。当用户提到"发推"、"发 Twitter"、"搜推文"、"看某个推文"、"查看推主历史"时使用。twitter 命令行已安装在 ~/.local/bin/twitter。
---

# Twitter CLI Skill

`twitter` CLI 已安装于 `~/.local/bin/twitter`，直接用 `twitter <command>` 调用即可。

## 核心原则

**遇到推文链接 → 先试 `twitter article`，不要开浏览器。**

> ⚠️ `browser_navigate` 是最后手段。只有当 `twitter article` 明确失败（报错或无输出）时才考虑浏览器。

| 场景 | 命令 |
|------|------|
| 推文链接 → 获取内容 | `twitter article <URL 或 ID>` |
| 搜推文 | `twitter search <关键词>` |
| 用户最新推文 | `twitter user-posts <@handle>` |
| 发推 | `twitter post "<内容>"` |
| 点赞 | `twitter like <ID>` |
| 转推 | `twitter retweet <ID>` |
| 搜索用户 | `twitter search --from <user>` |
| 时间线 | `twitter feed` |

| 场景 | 命令 |
|------|------|
| 推文链接 → 获取内容 | `twitter article <URL 或 ID>` |
| 搜推文 | `twitter search <关键词>` |
| 用户最新推文 | `twitter user-posts <@handle>` |
| 发推 | `twitter post "<内容>"` |
| 点赞 | `twitter like <ID>` |
| 转推 | `twitter retweet <ID>` |
| 搜索用户 | `twitter search --from <user>` |
| 时间线 | `twitter feed` |

## 常用命令详解

### 读取推文（最常用）

```bash
# 从 URL 或推文 ID 读取，返回 Markdown
twitter article <URL或ID> -m

# 输出 JSON
twitter article <ID> --json

# 保存到文件
twitter article <URL> -o /tmp/tweet.md --markdown
```

### 搜索

```bash
# 基础搜索
twitter search "AI news"

# 高级搜索
twitter search "from:treydtw" --since 2026-01-01
twitter search "python" --from elonmusk --min-likes 100
twitter search "新闻" --lang zh --since 2026-04-01
```

### 用户推文

```bash
# 获取用户最新推文（不加 @）
twitter user-posts treydtw --max 5

# JSON 输出
twitter user-posts treydtw --max 3 --json -o /tmp/posts.json
```

### 发推

```bash
twitter post "内容"
```

### 查看单条推文

```bash
# 先 search/feed 获取 INDEX，再用 show
twitter show <INDEX>
```

## 输出格式

| 参数 | 用途 |
|------|------|
| `--json` | 程序化处理 |
| `--yaml` | 备用格式 |
| `-m, --markdown` | Markdown，适合直接展示 |
| `-o <file>` | 保存到文件 |
| `--compact` | 紧凑输出，LLM 友好 |

## 陷阱

- `user-posts` 参数是 screen_name（不带 @）
- `article` 接受完整 URL 或纯数字 ID
- 涉及中文内容加 `--lang zh`
- 日期过滤用 `--since YYYY-MM-DD`
