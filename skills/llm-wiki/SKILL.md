---
name: llm-wiki
description: LLM Wiki 知识库编译与维护 — 当用户说「编译知识库」「更新知识库」「跑一次 lint」时使用。本 skill 封装了 LLM Wiki 的 ingest、lint、index 重建全流程。
---

# LLM Wiki 编译 Skill

> 本 skill 驱动知识库的自动化编译流程。适用于 cron 定时任务或手动触发。

## 知识库路径

```
知识库根目录：/vol1/1000/知识库/10-Base/
Raw 原料仓：   /vol1/1000/知识库/10-Base/01-Raw/
Inbox（新增）： /vol1/1000/知识库/10-Base/01-Raw/01-Inbox/
Wiki 层：       /vol1/1000/知识库/10-Base/02-Library/
摘要库：        /vol1/1000/知识库/10-Base/02-Library/01-Summaries/
概念库：        /vol1/1000/知识库/10-Base/02-Library/02-Concepts/
健康检查：      /vol1/1000/知识库/10-Base/02-Library/04-Health/
索引：          /vol1/1000/知识库/10-Base/02-Library/index.md
日志：          /vol1/1000/知识库/10-Base/02-Library/log.md
配置规范：      /vol1/1000/知识库/10-Base/CLAUDE.md
```

## 编译流程（Ingest）

### 第一步：扫描待处理文件

> ⚠️ **重要**：`grep -L` 的 exit code 含义与直觉相反——当文件**包含**匹配时返回 1，**不包含**时返回 0。
> 这导致 `find | xargs grep -L "status: done"` 的结果容易误判。
> **必须用 Python 做精确检查**，不要依赖 grep 的退出码。

```python
# 找出所有 NOT compiled: true 的 .md 文件（精确检查）
import os
inbox = "/vol1/1000/知识库/10-Base/01-Raw/01-Inbox/"
uncompiled = []
for f in sorted(os.listdir(inbox)):
    if not f.endswith(".md"):
        continue
    path = os.path.join(inbox, f)
    with open(path) as fh:
        content = fh.read()
    if "compiled: true" not in content:
        uncompiled.append(f)
# uncompiled 即为待处理文件列表
```

**判断标准**：严格以 `compiled: true` 在 frontmatter 中是否存在为准，而非 `status: done`（后者可能因引号格式导致漏检）。

### 第二步：对每篇 raw 执行编译

每篇 raw 产出一到两个文件：

**产物A → 02-Library/01-Summaries/**
- 文件名：`摘要_YYYY-MM-DD_<原文件名>.md`
- 内容格式严格遵循 CLAUDE.md 规范（frontmatter + 一句话结论 + 核心论述 + 关键证据 + 疑点 + 值得记住的点 + 关联概念）

**产物B → 02-Library/02-Concepts/**（仅当有真正新概念时）
- 检查现有 6 个概念是否已覆盖本文核心观点
- 如果没有，分配下一个序号（C-007 等）创建新概念文件
- 概念必须满足：有中文定义、有英文名、有证据来源、有使用场景、有至少一个关联概念
- 不满足则不创建，降级为摘要备注

### 第三步：标记完成

使用 `patch` tool 在 raw 文件 frontmatter 中设置 `compiled: true`：
- **已有 frontmatter**：在 `status: done` 后追加 `compiled: true`
- **无 frontmatter**（如旧文件漏填 metadata）：先在文件头部插入完整的 frontmatter block，再追加 `compiled: true`

> 注意：CLAUDE.md 规范明确禁止 metadata 不全的资料进入 Raw/。发现此类文件应一并补全。

### 第四步：更新 index.md

> **重要**：index.md 是知识库的导航入口。每次 ingest 后必须同步更新。
>
> **更新规则**：
> - 新摘要：追加到「2026年」摘要表顶部
> - 新概念：追加到概念表，并附上来源数
> - 最近更新表：追加本次 ingest entry

### 第五步：追加 log.md

```bash
# 或者直接追加到 log.md 末尾，格式：
## [YYYY-MM-DD] ingest | <文件名>
- 操作：处理 N 篇新 raw
- 新增摘要：N 条
- 新增概念：N 个（或「无新概念」）
```

---

## Lint 流程（健康检查）

### 触发条件

- 手动：`跑一次 lint`
- 定时：每周一 07:00

### 检查项

1. **概念链接完整性**：每个概念的 `[[C-XXX_xxx]]` 链接目标文件是否真实存在
2. **孤立概念**：没有任何链接的概念（无入链无出链）
3. **摘要-概念对应**：每条摘要是否有关联概念，概念是否对应真实摘要
4. **元数据完整性**：frontmatter 是否齐全（author、date、url、tags、status）

### 输出

在 `02-Library/04-Health/` 下生成健康报告：
- 文件名：`health_YYYY-WW.md`（周编号，可用 `date +%Y-%V`）
- 内容：问题列表 + 统计摘要 + 行动项

### 修复

lint 发现的问题，LLM 应立即修复（修正链接、补充关联），不要留到下次。

---

## 索引重建（Index Rebuild）

当 index.md 过于冗长或结构需要刷新时，执行重建：

```bash
# 调用重建脚本（见 scripts/rebuild_index.py）
python3 ~/.hermes/scripts/llm-wiki-rebuild-index.py
```

脚本从文件系统的实际内容生成新的 index.md，无需人工介入。

---

## 日志追加（Log Append）

每次操作后追加日志 entry，不覆盖历史。格式：

```markdown
## [YYYY-MM-DD] <type> | <描述>
- 操作：<具体做了什么>
- 新增摘要：N 条
- 新增概念：N 个
```

type 可选：`ingest` | `lint` | `compile` | `custom`

---

## 自动化 Cron 配置

建议配置两条 cron：

| 任务 | 时间 | 触发 |
|------|------|------|
| 每日编译 | 每天 01:00 | 扫描 inbox，处理新 raw，更新 index + log |
| 每周 lint | 每周一 07:00 | 健康检查 + 生成报告 + 修复问题 |

---

## 质量标准

- 每篇 raw 必须生成摘要（除非 frontmatter 不完整被退回）
- 概念冲突：保留其一，文件名加 `_v2`，在证据与来源中标注来源变更
- 禁止修改历史摘要内容，只覆盖更新
- 禁止删除任何 raw 文件
