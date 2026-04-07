---
name: task-sync
description: Obsidian tasknotes 文件管理 — 创建、更新、完成任务，直接写 md 文件到 00-Tasks/ 目录。当用户说「创建任务」「完成任务」「开始任务」时触发。
---

# Task Sync

以 Obsidian tasknotes 为单一真相源，通过直接读写 `00-Tasks/` 目录下的 markdown 文件来管理任务。

## 文件格式

任务文件路径：`/vol1/1000/知识库/00-Tasks/<文件名>.md`

```yaml
---
title: <任务标题>
status: open | done | cancel
priority: low | normal | high
tags:
  - task
scheduled: <YYYY-MM-DD>   # 可选
due: <YYYY-MM-DD>          # 可选
recurrence: <规则>         # 可选，如 DTSTART:20260407;FREQ=DAILY;INTERVAL=1
projects:
  - "<项目名>"              # 可选，Obsidian wiki 链接格式
discordThreadUrl: <url>   # 可选，不自动管理
dateCreated: <ISO时间>
dateModified: <ISO时间>
tasknotes_manual_order: "<序号>"
---

# <任务标题>
```

## 状态说明

| status | 含义 |
|--------|------|
| `open` | 未完成（新建任务默认） |
| `done` | 已完成 |
| `cancel` | 已取消 |

## 核心操作

### 1. 创建任务
**触发词**：`创建任务 <任务名> [优先级] [截止日期|scheduled|due]`

1. **生成文件名**：去掉或替换文件名中的特殊字符（emoji 保留，`/` → `·`）
2. **构建 frontmatter**：title, status=open, priority, scheduled/due, tags, dateCreated, dateModified
3. **写文件**：路径 `/vol1/1000/知识库/00-Tasks/<文件名>.md`
4. **写正文**：正文同标题（`# <任务名>`）

**优先级**：high / normal（默认）/ low
**日期**：scheduled 用于 tasknotes 日历视图，due 用于截止日期

### 2. 完成任务
**触发词**：`完成任务 <任务名>`

1. 用 `grep` 搜索 `00-Tasks/` 下 title 或文件名匹配的文件
2. 读取文件，修改 `status: open` → `status: done`，更新 `dateModified`
3. 写回文件

### 3. 取消任务
**触发词**：`取消任务 <任务名>`

1. 同上，修改 `status: cancel`

### 4. 查看任务
**触发词**：`查看任务`、`任务列表`

1. `grep -r "status: open" /vol1/1000/知识库/00-Tasks/*.md` 列出所有 open 任务
2. 返回文件名、title、priority、scheduled/due

### 5. 查找任务
**触发词**：`查找任务 <关键词>`

1. 用 grep 搜索文件名和 title 字段
2. 返回匹配结果

## 路径常量

```
TASKS_DIR="/vol1/1000/知识库/00-Tasks"
```

## 注意事项

- **不操作飞书**：已废弃 tasknotes → 飞书同步
- **不操作 Discord**：discordThreadUrl 字段由用户在 Obsidian 手动维护或通过其他机制写入
- **直接写文件**：用 write_file 工具，不走 API
- **文件名合法化**：emoji 保留，`/` → `·`，`\` → `·`，其余特殊字符去除或替换
- **精确匹配**：先试 exact match，找不到再模糊搜索
