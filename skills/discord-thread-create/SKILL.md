---
name: discord-thread-create
description: 在 Discord 当前频道创建子区（thread）。当用户说"开个讨论区"、"开个子区"、"创建线程"时使用。直接调用 Hermes Discord adapter 的原生方法，不依赖外部 token。
triggers:
  - 开个讨论区
  - 开个子区
  - 创建线程
  - 创建子区
  - 子区讨论
---

# discord-thread-create

在 Discord 当前频道创建子区（thread）。使用 Hermes 原生的 discord.py API，不调用 REST API。

## 实现方式

在 Hermes CLI 环境中，通过添加临时 handler 的方式在当前 channel 创建 thread：

```python
import asyncio
import sys
sys.path.insert(0, '/Users/Treydong/.hermes/hermes-agent')
from gateway.platforms.discord import DiscordAdapter
from gateway.config import load_gateway_config

async def create_thread(adapter: DiscordAdapter, channel_id: str, name: str, message: str = ""):
    """Create a thread in the given channel."""
    # Get the channel object from the guild
    guild = await adapter._client.fetch_guild(int(adapter._client.guilds[0].id))
    channel = await guild.fetch_channel(int(channel_id))
    
    # Create thread using discord.py native API
    thread = await channel.create_thread(
        name=name,
        auto_archive_duration=1440,
        message=message if message else None
    )
    return thread
```

## 限制

- **只能在已加入的服务器中使用** — adapter 必须已经连接 Discord
- thread 在当前频道（parent channel）中创建
- 需要调用 `channel.create_thread()` 方法

## 验证

创建后返回 thread 的链接，格式为：
`https://discord.com/channels/{guild_id}/{thread_id}`

---

## 关闭子区（Close Thread）

Discord 客户端的"关闭子区"执行两步：
1. **删除父频道里的 thread starter message**（发起消息，message ID = thread ID）
2. **Archive 线程**（`archived: true`）

**只 archive 不删消息**：线程会移到存档列表，但父频道主聊天区的入口消息仍然可见。

**正确做法**（两步都要）：
```bash
# 第一步：删除 thread starter message（需要父频道 ID + thread ID）
curl -X DELETE "https://discord.com/api/v9/channels/{parent_id}/messages/{thread_id}" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN"

# 第二步：archive 线程
/Users/Treydong/bin/discord-ops thread archive <thread_id>
```

**CLI 一键关闭**（如果已实现）：
```bash
/Users/Treydong/bin/discord-ops thread close <thread_id>
```

**重要**：任何发送到线程的新消息都会自动 unarchive 线程。关闭操作完成后不要在 thread 内发消息，否则线程重新激活。

**用户偏好**：用户要求"只执行/不要回复任何消息"时，执行完不输出任何文字。
