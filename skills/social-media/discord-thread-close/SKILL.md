---
name: discord-thread-close
description: 彻底关闭 Discord 子区（thread），让入口完全消失。使用 /Users/Treydong/bin/discord-ops CLI 执行。
---

# Discord 子区彻底关闭

## 问题背景

- `archived: true` → 线程移到存档列表，但父频道里的 thread starter message（发起消息）还在，所以主聊天区还有入口
- Discord 客户端的"关闭子区" = 删除发起消息 + archive 线程

## 正确操作步骤

1. **删除 thread starter message**（父频道里 ID = thread_id 的那条消息）→ 入口消息消失
2. **Archive 线程** → 移到存档列表

## CLI 方式（推荐）

```bash
/Users/Treydong/bin/discord-ops close <THREAD_ID>
```

## 关键规则

**用户说"只执行/不要回复任何消息"时**：执行完命令后**不输出任何文字**，直接沉默。工具结果回到上下文，但我看到后不能解读和回复——这是行为习惯问题，不是代码强制。