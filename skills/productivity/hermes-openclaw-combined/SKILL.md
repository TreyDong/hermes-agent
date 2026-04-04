---
name: hermes-openclaw-combined
description: 以 Hermes 为主力、OpenClaw 为渠道适配器的双 Agent 协作架构
---

# Hermes + OpenClaw 协作架构

## 背景
用户同时安装了 Hermes 和 OpenClaw。认为 Hermes 执行能力更强，倾向以 Hermes 为主力。

## 推荐架构

### 以 Hermes 为核心（推荐）
```
Hermes = 主力执行者 (监督 + 执行 + 记忆 + cron)
OpenClaw = 渠道适配器 (WhatsApp/iMessage 等 Hermes 没有的渠道)
```

### 架构图
```
用户 → Hermes (复杂任务/研究/cron)
     → OpenClaw (仅做 Hermes 没有的渠道接入)
```

### OpenClaw 专用渠道（ Hermes 没有的）
- iMessage (BlueBubbles)
- WhatsApp (某些特定场景)
- Signal
- Matrix/Nostr
- macOS 原生桌面 App

### Hermes 优势覆盖
- Discord / Telegram / Slack → 两者都能，但 Hermes 更强
- 代码执行 / 研究分析 / 记忆系统
- subagent 并行任务
- cron 定时任务
- 多模型路由 (OpenRouter 200+)
- MCP 协议扩展

## 协作模式（参考 x.com/gkisokay 的设计）

### 机器间通讯协议（4 个 Intent Markers）
| Marker | 含义 |
|---|---|
| `[ACK]` | 任务完成，终止对话 |
| `[STATUS_REQUEST]` | 请求状态更新 |
| `[REVIEW_REQUEST]` | 请求人工审核 |
| `[FYI]` | 通知，无需回复 |

### 终止规则
- 最多 3 条消息
- 收到 `[ACK]` 立即停止

### 实际配置
1. Discord 专用频道 `#operator-ai` 做机器间通讯
2. OpenClaw 接收消息后判断：复杂任务 → Hermes
3. Hermes 处理完 → 结果回传 → OpenClaw 投递

## OpenClaw 诊断流程（2026-04-03）

**快速诊断命令：**
```bash
openclaw status          # 查看 gateway/agents 运行状态
openclaw logs --lines 50  # 最近日志
ps aux | grep openclaw   # 进程是否存在
```

**常见挂掉原因：**
1. Discord bot token 过期/失效 → `openclaw config get channels.discord.token` 检查
2. 端口冲突（默认 18789）→ `lsof -i :18789`
3. 配置 JSON 格式错误 → `openclaw config validate`
4. 依赖服务未启动（如 Redis/数据库）
5. 内存不足 / OOM

## Skills 禁用建议
用户可能想禁用的（安全性/隐私/用不到）：
- `godmode` - 越狱/red-teaming 工具
- `claude-code` / `codex` / `opencode` - 其他 Agent CLI
- `pokemon-player` / `minecraft-modpack-server` - 游戏相关
- `obliteratus` - 去除模型限制

## 参考资料
- x.com/gkisokay 发布的协作方案 thread: https://x.com/i/status/2037902655016804496
