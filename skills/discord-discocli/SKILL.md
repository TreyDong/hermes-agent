---
name: discord-discocli
description: Discord CLI 工具 —— 通过 discocli 操作 Discord：读取频道/子区消息、同步、搜索、发消息、MCP server。适合需要从终端操作 Discord 的任务。
category: social-media
---

# Discord CLI (discocli)

通过 `discocli` 在终端操作 Discord，支持 bot token 认证、MCP server 模式。

## 安装

```bash
# Go 构建（已有 Go 环境）
cd /tmp && git clone https://github.com/virat-mankali/discord-cli
cd discord-cli && go build -o discocli ./cmd/discocli/
cp discocli ~/bin/discocli

# NAS 已在 /home/banana/bin/discocli
```

## 认证

```bash
# 写入 token（token 格式：bot\nTOKEN）
echo -e "bot\nYOUR_BOT_TOKEN" > ~/.discocli/token
chmod 600 ~/.discocli/token
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `discocli whoami` | 显示当前登录用户 |
| `discocli guilds` | 列出所有服务器 |
| `discocli channels --guild "服务器名"` | 列出服务器下的频道 |
| `discocli sync --guild "服务器名" --channel "频道名"` | 同步指定频道消息到本地 SQLite |
| `discocli sync --follow --guild "服务器名" --channel "频道名"` | 实时监听新消息 |
| `discocli search "关键词"` | 搜索已同步消息 |
| `discocli send --to "#频道名" --text "内容"` | 发送消息 |
| `discocli send --to "thread_id" --text "内容"` | 发送消息到 thread |
| `discocli serve` | 启动 MCP server（给 AI agent 用）|

## 子区操作

```bash
# 获取子区 ID：从 Discord URL 提取
# URL 格式：https://discord.com/channels/SERVER_ID/CHANNEL_ID
# 子区是 type=11 的 channel

# 发消息到子区
discocli send --to "子区ID" --text "消息内容"

# 同步子区消息
discocli sync --channel "子区名" --guild "服务器名"
```

## discocli auth（交互式，需要手动输入）

```bash
# 交互式认证（需要 terminal 支持）
discocli auth
# 选择 token 类型 (bot/user)
# 输入 token
```

## MCP Server 模式

在 AI agent 环境中，将 discocli 作为 MCP server 使用：

```json
{
  "mcpServers": {
    "discocli": {
      "command": "/home/banana/bin/discocli",
      "args": ["serve"],
      "env": {},
      "disabled": false,
      "autoApprove": ["search_messages", "list_guilds", "list_channels", "get_sync_status"]
    }
  }
}
```

可用 MCP tools：
- `search_messages` — 全文搜索
- `list_guilds` — 列出服务器
- `list_channels` — 列出频道
- `send_message` — 发消息（需确认）
- `sync_channel` — 同步频道

## 已知问题

- auth 命令需要交互式 terminal，直接 `--token` 不可用
- token 文件格式不是 JSON，是 `type\ntoken`
- `sync --follow` 需要持续运行，适合后台任务
