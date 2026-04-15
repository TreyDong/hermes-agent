---
name: task-sync
description: Obsidian tasknotes 文件管理 — 创建、更新、完成任务，直接写 md 文件到 01-Tasks/ 目录。当检测到用户意图创建/完成/取消/查看任务时触发。
---

# Task Sync

以 Obsidian tasknotes 为单一真相源，通过直接读写 `01-Tasks/` 目录下的 markdown 文件来管理任务。

## 文件格式

任务文件路径：`/vol1/1000/知识库/01-Tasks/<文件名>.md`

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
projectPath: /vol2/1000/项目库/<项目名>/  # 可选，关联实际项目目录（归档后在已归档下）
projects:
  - "<项目名>"              # 可选，Obsidian wiki 链接格式
discordThreadUrl: <url>   # 可选，不自动管理
dateCreated: <ISO时间>
dateModified: <ISO时间>
tasknotes_manual_order: "<序号>"
---

# <任务标题>
```

## TaskNotes 状态（来源：插件 data.json）

TaskNotes 插件定义的状态是唯一的真相来源，脚本必须严格对齐：

| status | isCompleted | 说明 |
|--------|------------|------|
| `open` | false | 规划中 |
| `in-progress` | false | 进行中 |
| `done` | true | 已完成 |
| `cancel` | true | 已取消 |

**禁止使用 `completed`——TaskNotes 不定义这个值。** 脚本里的 `is_completed_status()` 必须只检查 `done` 和 `cancel`。

## 脚本执行原则

当脚本对外写状态标记（如 `discordArchived: true`）前，**必须验证底层操作成功才能写入本地状态**。否则会出现 frontmatter 显示已完成但 Discord 实际未归档的不一致。Discord CLI 调用使用 `CompletedProcess` 返回值检查 returncode，不依赖 stdout 内容判断成功与否。

## 路径常量

```
TASKS_DIR="/vol1/1000/知识库/01-Tasks"
```
PROJECT_REPO="/vol2/1000/项目库"
PROJECT_ARCHIVED="/vol2/1000/项目库/已归档"
```

## 核心操作

### 1. 创建任务

**触发检测**：检测以下模式的任意一种即触发：
- `创建任务` / `新建任务` / `加个任务` / `添加任务` / `我要做...` / `想做...` / `应该做...`
- 意图词：create, add, new task, todo
- **注意**：当用户说 `项目` 时，优先触发「创建项目」逻辑（见下）

**参数提取**（按优先级）：
1. 引号或书名号内的内容：`"任务名"` / `「任务名」`
2. `叫/名叫/名称是/名为` 后面的内容
3. `任务` 后面的第一个名词短语
4. 整句话去掉意图词后的剩余部分

**优先级提取**：
- `高` / `重要` / `紧急` / `!` / `urgent` → `high`
- `低` / `次要` / `不急` → `low`
- 默认 → `normal`

**日期提取**（支持自然语言）：
- `今天` → `YYYY-MM-DD`
- `明天` → +1 day
- `后天` → +2 days
- `这周末` → upcoming Saturday
- `下周一` → upcoming Monday
- `X号` / `X日` → 本月X号（若已过则下月）
- `MM-DD` / `YYYY-MM-DD` → 直接解析

**操作流程**：
1. 提取任务名；若无法提取，询问用户
2. 生成合法文件名（emoji 保留，`/` → `·`，`\` → `·`，其余特殊字符去除）
3. 构建 frontmatter（status=open, priority, scheduled/due, tags, dateCreated, dateModified）
4. 写入文件
5. 返回创建确认（含文件路径和任务名）

### 1.5 创建项目（含任务）

**触发检测**：
- `创建项目` / `新建项目` / `做个项目` / `项目叫` / `项目名称`
- 或任务描述中包含 `项目` 关键词且语气偏长期/系统性（如 `我要做一个XX项目`）

**路径约定**：
- **实际项目目录**：`/vol2/1000/项目库/<项目名>/`（默认，项目文件存放处）
- **已归档项目目录**：`/vol2/1000/项目库/已归档/<项目名>/`
- **Obsidian 入口文档**：`/vol1/1000/知识库/02-Projects/<项目名>.md`（仅一个 md 文件，作为入口引用）

**操作流程**：
1. **提取项目名**：引号/书名号内 > `叫/名叫/名称是` 后 > `项目` 后的名词
2. **创建实际项目目录**：`/vol2/1000/项目库/<项目名>/`
3. **初始化 README.md**：在 `/vol2/1000/项目库/<项目名>/README.md` 写入项目概述模板
4. **创建 Obsidian 入口文档**：在 `/vol1/1000/知识库/02-Projects/<项目名>.md` 写入 Obsidian wiki 链接格式 `[[file:///vol2/1000/项目库/<项目名>/README.md]]`，并附项目基本信息
5. **创建关联任务**：在 `01-Tasks/` 下创建任务文件，frontmatter 添加 `projectPath: /vol2/1000/项目库/<项目名>/`
6. **返回确认**：告知 Obsidian 入口文档路径、实际项目路径和任务路径

### 1.6 归档项目

**触发检测**：`归档项目` / `项目归档` / `把XX归档` / `XX归档`

**操作流程**：
1. **查找项目**：在 `/vol2/1000/项目库/` 下找到匹配的项目目录（不含 `已归档/`）
2. **移动目录**：将 `/vol2/1000/项目库/<项目名>/` 移动到 `/vol2/1000/项目库/已归档/<项目名>/`
3. **更新 Obsidian 入口文档**：将 wiki 链接指向 `已归档/<项目名>/README.md`
4. **更新任务文件**：将 frontmatter 中的 `projectPath` 改为 `/vol2/1000/项目库/已归档/<项目名>/`
5. **返回确认**：告知归档后的路径

### 2. 完成任务

**触发检测**：`完成` / `做完了` / `搞定了` / `结束` / `done` + 任务名

**操作流程**：
1. 搜索 `01-Tasks/` 下 title 或文件名匹配的文件
2. 读取文件，修改 `status: open` → `status: done`，更新 `dateModified`
3. 写回文件
4. 返回完成确认

### 3. 取消任务

**触发检测**：`取消` / `删除` / `不要了` / `算了` + 任务名

**操作流程**：
1. 同上，修改 `status: cancel`

### 4. 查看任务列表

**触发检测**：`查看任务` / `任务列表` / `还有什么` / `待办` / `todos`

**操作流程**：
1. `grep -r "status: open" /vol1/1000/知识库/01-Tasks/*.md`
2. 返回文件名、title、priority、scheduled/due，按 scheduled/due 排序

### 5. 查找任务

**触发检测**：`查找任务` / `搜索任务` / `有没有` + 关键词

**操作流程**：
1. 搜索文件名和 title 字段
2. 返回匹配结果

## 文件名合法化规则

- emoji：保留
- `/` → `·`
- `\` → `·`
- 其余特殊字符：去除
- 空格：保留或转 `-`

## 注意事项

- **不操作飞书**：已废弃 tasknotes → 飞书同步
- **不操作 Discord**：discordThreadUrl 字段由用户在 Obsidian 手动维护
- **直接写文件**：用 write_file 工具
- **精确匹配优先**：先试 exact match，找不到再模糊搜索
- **无任务名时询问**：不要猜测任务名
