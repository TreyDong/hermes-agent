---
name: task-sync-scan-debug
description: TaskNotes sync脚本调试与修复记录 — frontmatter和Discord状态不一致的根因与解决方案
category: devops
---

# task-sync-scan.py 调试与修复记录

## 已知 Bug

### Bug: 静默归档失败导致 frontmatter 和 Discord 状态不一致

**症状**：任务 frontmatter 里 `discordArchived: true`，但 Discord thread 没有归档，状态也没变成已完成。

**根因**：
- `discord_cli()` 返回 string（命令输出），不是 `CompletedProcess` 对象
- `archive_discord_thread()` 不检查返回值，直接当成功处理
- 脚本更新了 frontmatter 写 `discordArchived: true`，但 Discord API 调用实际失败了
- 下次运行脚本看到 `archived=true` 就跳过，永不重试

**修复**：
1. `discord_cli()` 返回 `subprocess.run()` 的完整 result 对象
2. `archive_discord_thread()` 返回 bool，成功才写 frontmatter
3. 主循环确认返回值后再写 `discordArchived: true`

```python
def discord_cli(*args) -> CompletedProcess:
    """Discord CLI wrapper — returns CompletedProcess, not string."""
    cmd = [str(DISCORD_CLI_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

def archive_discord_thread(thread_id: str) -> bool:
    result = discord_cli("thread", "archive", thread_id)
    return result.returncode == 0
```

## TaskNotes 状态定义（来自 data.json）

```json
"customStatuses": [
  { "id": "open",        "value": "open",        "isCompleted": false },
  { "id": "in-progress", "value": "in-progress", "isCompleted": false },
  { "id": "done",        "value": "done",        "isCompleted": true  },
  { "id": "cancel",      "value": "cancel",      "isCompleted": true  }
]
```

**注意**：无 `completed` 值，脚本里不要使用。

## 调试命令

```bash
# 手动跑一次
/usr/bin/python3 /vol1/1000/hermes/scripts/task-sync-scan.py

# 查看 Discord thread 状态
~/bin/discord-cli thread list --guild 1453031874082373687

# 直接归档一个 thread
~/bin/discord-cli thread archive <thread_id>

# 查任务 frontmatter
grep -r "discordArchived" /vol1/1000/知识库/01-Tasks/
```

## 关键文件

- 脚本：`/vol1/1000/hermes/scripts/task-sync-scan.py`
- 任务目录：`/vol1/1000/知识库/01-Tasks/`
- Discord CLI：`~/bin/discord-cli`
- Discord 服务器香蕉：1453031874082373687
