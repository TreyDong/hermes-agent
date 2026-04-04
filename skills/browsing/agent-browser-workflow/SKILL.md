---
name: agent-browser-workflow
description: Browser automation workflow using agent-browser (skills.sh/vercel-labs/agent-browser). Control local or NAS Chrome via refs interaction.
---

# agent-browser Workflow

浏览器自动化操作流程，基于 skills.sh/vercel-labs/agent-browser。

## 环境

| 端 | Chrome 端口 | agent-browser 路径 | 状态 |
|---|---|---|---|
| Mac | 9223 | `/usr/local/bin/agent-browser` | 已装 |
| NAS (飞牛OS) | 9222 | `~/.npm-global/bin/agent-browser` | 已装 |

## 基本命令

```bash
# Mac 本地
agent-browser open "https://..."
agent-browser fill @e13 "搜索词"
agent-browser click @e13
agent-browser snapshot
agent-browser screenshot /tmp/out.png

# NAS（通过SSH）
sshpass -p '11114444' ssh -o StrictHostKeyChecking=no -p 2222 banana@192.168.31.154 \
  "agent-browser open 'https://...'"
```

## 截图回传 Mac

NAS 截图生成在 NAS 本地，需要 `scp` 回传：

```bash
sshpass -p '11114444' scp -P 2222 banana@192.168.31.154:/tmp/shot.png /tmp/nas-shot.png
```

## 典型工作流（NAS）

1. SSH 打开页面
2. snapshot 查看所有元素 refs
3. fill/click 操作
4. screenshot 截图
5. scp 回传截图

## 清理残留进程

```bash
pkill -f agent-browser
```
