---
name: task-sync
description: Discord帖子 ↔ 飞书任务 ↔ 本地文档 三方同步。当用户说「创建任务」「创建子任务」「开始任务」「完成任务」时触发。
---

# Task Sync

本地文档 `/vol1/1000/知识库/base/TASK.md` 作为唯一真相源，驱动 Discord Forum 帖子和飞书任务的状态联动。

## 文档格式

```markdown
# 任务同步表

🟡 进行中：2 | ✅ 已完成：3 | 📋 总计：5

---

# 项目A

| 任务名 | Discord帖子ID | 飞书任务ID | 状态 | 优先级 | 截止日期 | 创建时间 |
|--------|---------------|------------|------|--------|----------|----------|
| [ ] 任务1 | 123456 | t_abc | 进行中 | 高 | 2026-04-10 | 2026-04-05 |
| [ ] 　└ 子任务1-1 | 789 | t_def | 规划中 | 中 | 2026-04-12 | 2026-04-06 |

# 项目B

| 任务名 | Discord帖子ID | 飞书任务ID | 状态 | 优先级 | 截止日期 | 创建时间 |
|--------|---------------|------------|------|--------|----------|----------|
| [x] 任务2 | 456 | t_ghi | 已完成 | 低 | 2026-04-08 | 2026-04-03 |
```

- `[ ]` = 未完成（规划中/进行中）
- `[x]` = 已完成
- 任务名中包含 `└` 表示是子任务，归属上级任务

## Discord 标签映射

| 状态 | 标签ID |
|------|--------|
| 规划中 | 1490190116835037305 |
| 进行中 | 1490190119905263899 |
| 已完成 | 1490190125685014569 |
| 暂停 | 1490190127753072691 |

| 优先级 | 标签ID |
|--------|--------|
| 高优先级 | 1490190186066350221 |
| 中优先级 | 1490190188847169546 |
| 低优先级 | 1490190190805782559 |

## Discord CLI

```bash
# 查看可用标签
discordctl tag list --channel 1490189325646696508

# 创建帖子
discordctl thread create --channel 1490189325646696508 \
  --name "<任务名>" \
  --content "<正文>" \
  --tags "<tag_ids>"

# 更新标签
discordctl thread update --thread <ID> --tags "<tag_ids>"

# 归档帖子（不推荐用于 Forum 帖子，用 send_message 按钮替代）
discordctl thread archive --thread <ID>
```

**注意**：关闭 Forum 帖子请用 `send_message` 发送关闭确认按钮（见"完成任务"流程），
不要直接用 `discordctl thread archive`。

## 飞书任务 CLI

```bash
# 创建主任务
lark-cli task +create --summary "<任务名>" --description "<描述>" --due "<YYYY-MM-DD>"

# 创建子任务（需先知道父任务 guid）
lark-cli task subtasks create --task-guid <父任务guid> --summary "<子任务名>"

# 完成任务
lark-cli task +complete --task-id <飞书任务ID>
```

## 1. 创建项目
**触发词**：`创建项目 <项目名>`

**步骤**：
1. 在 TASK.md 末尾追加 `# <项目名>` 和表头

## 2. 创建任务
**触发词**：`创建任务 <项目名/任务名> [优先级] [截止日期]`

**步骤**：
1. 读文档，找到对应项目段落，追加行（`[ ] <任务名>`）
2. `discordctl thread create` → 创建 Discord 帖子
3. `lark-cli task +create` → 创建飞书主任务
4. 回填 Discord帖子ID 和 飞书任务ID
5. 更新顶部汇总行计数

**正文模板**：
```
📋 **<项目名> / <任务名>**

**状态：** 🟡 规划中
**优先级：** 🔴 高
**截止：** 2026-04-10
```

## 3. 创建子任务
**触发词**：`创建子任务 <项目名/任务名-子任务名> [优先级] [截止日期]`

**步骤**：
1. 读文档，找到父任务行，追加子任务行（`[ ] 　└ <子任务名>`）
2. `discordctl thread create` → 创建 Discord 帖子（子任务一般不需要单独帖子，可选跳过）
3. `lark-cli task subtasks create` → 创建飞书子任务（关联父任务 guid）
4. 回填飞书任务ID（子任务不需要 Discord 帖子ID）
5. 更新顶部汇总行计数

## 4. 开始任务
**触发词**：`开始任务 <项目名/任务名>`

**步骤**：
1. 文档 `[ ]` → `[ ]`（状态改「进行中」，标记不变）
2. `discordctl thread update` → Discord 标签改为「进行中」

## 5. 完成任务
**触发词**：`完成任务 <项目名/任务名>`

**步骤**：
1. 文档 `[ ]` → `[x]`
2. **发送 Discord 关闭确认按钮**：
   ```
   send_message(
     target="discord:<Discord帖子ID>",
     message="🧵 确定要关闭该帖子吗？关闭后将归档此讨论。",
     components=[
       {
         "type": 1,
         "components": [
           {"type": 2, "style": 4, "label": "🔒 确认关闭", "custom_id": "close_thread_btn"},
           {"type": 2, "style": 2, "label": "取消", "custom_id": "cancel_close_btn"}
         ]
       }
     ]
   )
   ```
   - 用户点击「🔒 确认关闭」→ Discord 帖子归档（gateway `on_interaction` 自动处理）
   - 用户点击「取消」→ gateway 返回"已取消"，帖子保持开放
3. `lark-cli task +complete --task-id <飞书任务ID>` → 完成飞书任务
4. 更新顶部汇总行计数

**注意**：如果任务没有 Discord 帖子ID（子任务等），跳过步骤 2。

## 汇总行更新规则

```
🟡 进行中：<所有 [ ] 行的数量>
✅ 已完成：<所有 [x] 行的数量>
📋 总计：<两者之和>
```

## 环境要求

- `~/bin/discordctl`（Python 3，pip install requests）
- `lark-cli` 已配置任务权限
- 文档路径 `/vol1/1000/知识库/base/TASK.md`

## 注意事项

- 匹配任务时用 `项目名/任务名` 精确匹配
- 子任务的飞书 `task_id` 格式不同于主任务
- 如果任务没有 Discord 帖子ID，则跳过 Discord 相关操作
- 每次操作后必须回填 IDs 到文档
