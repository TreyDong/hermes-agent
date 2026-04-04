---
name: discord-channel-manager
description: 使用 Discord 官方 REST API 创建/删除/编辑频道。当用户要求创建 Discord 频道、删除频道、修改频道名称/权限时使用。Token 自动从 ~/.openclaw/openclaw.json 读取。必须用 curl（不是 Python urllib），因为需要走代理。
triggers:
  - 创建 Discord 频道
  - 新建频道
  - 删除 Discord 频道
  - 修改频道名称
  - Discord 频道管理
---

# discord-channel-manager

使用 Discord Bot Token 调用官方 REST API 管理频道（创建/删除/编辑）。

## 重要：必须用 curl + 代理

Discord 请求必须走 `http://127.0.0.1:7897` 代理，且必须用 curl（Python urllib 会被 Cloudflare 拦截返回 1010）。

## Token 获取

自动从 OpenClaw 配置读取（使用 symphony bot）：
```python
import json
with open('/Users/Treydong/.openclaw/openclaw.json') as f:
    config = json.load(f)
token = config['channels']['discord']['accounts']['symphony']['token']
```

**已知 Guild ID**: `1453031874082373687`（banana_labo 服务器）

## API 调用模板

### Python（execute_code 中使用）

```python
import subprocess, json

def discord_api(method, path, token, data=None):
    proxy = 'http://127.0.0.1:7897'
    cmd = ['curl', '-s', '-x', proxy,
           '-H', f'Authorization: Bot {token}',
           '-H', 'Content-Type: application/json']
    if method == 'POST':
        cmd += ['-X', 'POST']
        if data:
            cmd += ['-d', json.dumps(data)]
    elif method == 'PATCH':
        cmd += ['-X', 'PATCH']
        if data:
            cmd += ['-d', json.dumps(data)]
    elif method == 'DELETE':
        cmd += ['-X', 'DELETE']
    cmd.append(f'https://discord.com/api/v10{path}')
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        return json.loads(result.stdout)
    except:
        return {'raw': result.stdout[:200]}

# 用法
token = 'TOKEN'
guild_id = '1453031874082373687'
result = discord_api('GET', f'/guilds/{guild_id}/channels', token)
```

### Shell 中直接用

```bash
TOKEN="symphony_token"
PROXY="http://127.0.0.1:7897"
GUILD_ID="1453031874082373687"

# 列出频道
curl -s -x "$PROXY" -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/guilds/$GUILD_ID/channels"

# 创建频道
curl -s -x "$PROXY" -X POST \
  -H "Authorization: Bot $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "频道名", "type": 0, "parent_id": "父分类ID"}' \
  "https://discord.com/api/v10/guilds/$GUILD_ID/channels"

# 编辑频道
curl -s -x "$PROXY" -X PATCH \
  -H "Authorization: Bot $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "新名称"}' \
  "https://discord.com/api/v10/channels/频道ID"

# 删除频道
curl -s -x "$PROXY" -X DELETE \
  -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/channels/频道ID"
```

## 已知频道结构

```
HQ (category)
  └── general (text)

Work (category)
  ├── lab (text)
  ├── content (text)
  ├── coding (text)
  ├── investing (text)
  ├── ops (text)
  └── task-board (thread)

System (category)
  └── [voice channels for agent status]

Feeds (category)
  ├── intel (text)
  ├── alerts (text)
  └── logs (text)

Voice (category)
  └── lounge (voice)

Archive (category)
  ├── thinking (text)
  ├── ideas (text)
  └── knowledge (text)
```

## 频道 type 值

- `0` — 文字频道
- `2` — 语音频道
- `4` — 分类（Category）
- `11` — Forum 频道
- `15` — 动态频道（线程）

## 常用操作

### 创建频道

```python
result = discord_api('POST', f'/guilds/{guild_id}/channels', token, {
    'name': '频道名称',
    'type': 0,
    'parent_id': '1474994305184825435',  # Work category
    'topic': '主题描述（可选）'
})
```

### 编辑频道名称/主题

```python
result = discord_api('PATCH', f'/channels/{channel_id}', token, {
    'name': '新名称',
    'topic': '新主题'
})
```

### 删除频道

```python
result = discord_api('DELETE', f'/channels/{channel_id}', token)
```

## 关闭线程的正确方式

**✅ 推荐：使用 /Users/Treydong/bin/discord-ops CLI（唯一推荐方式）**

```bash
# 直接关闭线程（删除入口消息 + archive 一次性完成）
/Users/Treydong/bin/discord-ops close <THREAD_ID> [PARENT_ID]
```

Discord 客户端"关闭子区"执行两步操作，CLI 已封装：

1. **删除 thread starter message**（入口消息，ID = 线程 ID）
2. **archive 线程**

只做 archive 不删入口 → 线程移到存档列表，但主聊天区入口消息还在（thread pill 仍然可点）。两者都做 = 和 Discord 客户端行为完全一致。

**Discord 机制提醒：**
- 在线程内发消息会自动 unarchive
- 测试时不能在目标线程内发消息
- `locked: true` 会阻止成员重新打开线程（一般不需要）

### 验证是否成功
```bash
# 查存档列表
curl -s -x "$PROXY" -H "Authorization: Bot $TOKEN" \
  "https://discord.com/api/v10/channels/$PARENT_ID/threads/archived/public" | \
  python3 -c "import sys,json; threads=json.load(sys.stdin)['threads']; print('CLOSED' if any(t['id']=='$THREAD_ID' for t in threads) else 'OPEN')"
```

已知 Guild ID: `1453031874082373687`（banana_labo）

## 注意事项

- 速率限制：每个 token 每秒最多 50 次请求，批量操作时加 `sleep 0.5`
- 权限要求：Bot 需要 `管理频道` 权限
- 创建后无法直接指定位置，用 PATCH `position` 字段调整
