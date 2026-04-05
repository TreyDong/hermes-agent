#!/usr/bin/env python3
"""
LLM Wiki Index Rebuild Script
Regenerates index.md from the actual file system state.
Run this after bulk operations or when index.md is stale.

Usage:
  python3 ~/.hermes/scripts/llm-wiki-rebuild-index.py
"""

import os
import re
from datetime import datetime

BASE = "/vol1/1000/知识库/10-Base"
LIB = f"{BASE}/02-Library"
SUMMARIES_DIR = f"{LIB}/01-Summaries"
CONCEPTS_DIR = f"{LIB}/02-Concepts"
QA_DIR = f"{LIB}/03-QA"
HEALTH_DIR = f"{LIB}/04-Health"
INDEX_PATH = f"{LIB}/index.md"

today = datetime.now().strftime("%Y-%m-%d")

def get_frontmatter(content, field):
    m = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
    return m.group(1).strip() if m else ""

def get_conclusion(content):
    lines = content.split('\n')
    in_meta = False
    for line in lines:
        if line.strip() == '---':
            in_meta = not in_meta
            continue
        if in_meta:
            continue
        if line.startswith('## ') or line.startswith('# '):
            continue
        if line.strip():
            return line.strip()[:80]
    return ""

# ── Scan Concepts ──────────────────────────────────────────
concept_files = sorted(os.listdir(CONCEPTS_DIR))
concepts = []
for f in concept_files:
    if not f.endswith('.md'):
        continue
    path = f"{CONCEPTS_DIR}/{f}"
    with open(path) as fp:
        content = fp.read()
    concepts.append({
        'file': f,
        'id': get_frontmatter(content, 'concept_id'),
        'name': get_frontmatter(content, 'name'),
        'name_en': get_frontmatter(content, 'name_en'),
        'tags': get_frontmatter(content, 'tags'),
        'updated': get_frontmatter(content, 'updated'),
        'sources': get_frontmatter(content, 'sources'),
        'status': get_frontmatter(content, 'status'),
        'content': content,
    })

# ── Scan Summaries ─────────────────────────────────────────
summary_files = sorted(os.listdir(SUMMARIES_DIR), reverse=True)
summaries = []
seen = set()
for f in summary_files:
    if not f.endswith('.md'):
        continue
    path = f"{SUMMARIES_DIR}/{f}"
    with open(path) as fp:
        content = fp.read()
    author = get_frontmatter(content, 'author')
    date = get_frontmatter(content, 'date')
    key = (date, author)
    if key in seen:
        continue
    seen.add(key)
    conclusion = get_conclusion(content)
    summaries.append({
        'file': f,
        'author': author,
        'date': date,
        'conclusion': conclusion,
    })

# ── Scan Health Reports ────────────────────────────────────
health_files = sorted(os.listdir(HEALTH_DIR), reverse=True)
healths = []
for f in health_files:
    if not f.endswith('.md'):
        continue
    path = f"{HEALTH_DIR}/{f}"
    with open(path) as fp:
        content = fp.read()
    date = get_frontmatter(content, '检查日期')
    healths.append({'file': f, 'date': date})

# ── Scan Log ───────────────────────────────────────────────
log_path = f"{LIB}/log.md"
recent_log = ""
if os.path.exists(log_path):
    with open(log_path) as fp:
        lines = fp.readlines()
    # Get last 10 entries
    entries = []
    current = []
    for line in lines:
        if line.startswith('## ['):
            if current:
                entries.append(''.join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append(''.join(current))
    recent_log = '\n'.join(entries[-6:])  # last 6 entries

# ── Build Concept Table ────────────────────────────────────
concept_table = "| ID | 名称 | 英文名 | 标签 | 更新 | 来源数 | 状态 |\n|----|------|--------|------|------|--------|------|"
concept_rows = []
for c in sorted(concepts, key=lambda x: x['id']):
    link_name = c['file'].replace('.md', '')
    row = f"| [[{link_name}]] | {c['name']} | {c['name_en']} | {c['tags']} | {c['updated']} | {c['sources']} | {c['status']} |"
    concept_rows.append(row)
concept_table += "\n" + "\n".join(concept_rows)

# ── Build Recent Summaries ─────────────────────────────────
recent_sum_table = "| 日期 | 作者 | 一句话结论 |\n|------|------|-----------|"
for s in summaries[:20]:
    conclusion = s['conclusion'].replace('|', '\\|')[:70]
    recent_sum_table += f"\n| {s['date']} | {s['author']} | {conclusion}… |"

# ── Build Health Table ─────────────────────────────────────
health_table = "| 周次 | 日期 | 状态 |\n|------|------|------|"
for h in healths[:10]:
    week = h['file'].replace('health_', '').replace('.md', '')
    health_table += f"\n| {week} | {h['date']} | [[{h['file']}]] |"

# ── Assemble index.md ──────────────────────────────────────
index_content = f"""---
title: 知识库索引
description: LLM Wiki 知识库页面导航索引
updated: {today}
---

# 知识库索引

> 本文件是 LLM Wiki 知识库的门户索引。LLM 回答查询时首先读取此文件定位相关页面。
> 页面内容按分类组织，使用 obsidian `[[双向链接]]` 语法。
>
> ⚠️ 本文件由 `llm-wiki-rebuild-index.py` 脚本自动重建，最后运行：{today}

---

## 概念（{len(concepts)}个）

> 已被内化、形成判断的核心概念条目

{concept_table}

**孤立概念警告**：C-002、C-003、C-004 暂无交叉链接，建议定期建立关联。

---

## 摘要库（{len(summaries)}篇）

> Raw 资料的结构化摘要缓存，按日期倒序（去重后）

{recent_sum_table}

> 查看完整历史摘要：按日期目录浏览 `02-Library/01-Summaries/`

---

## QA 沉淀（{len(os.listdir(QA_DIR)) if os.path.exists(QA_DIR) else 0}条）

> 复杂推理对话的结论归档，追加不覆盖

暂无 QA 条目。**待积累。**

---

## 健康检查报告

{health_table}

---

## 最近更新（来自 log.md）

{recent_log if recent_log else '_暂无历史日志_'}

---

## 快速导航

- **Raw 原料仓**：`01-Raw/01-Inbox/`（新资料）| `01-Raw/99-Archived/`（历史存档）
- **Wiki 编译层**：`02-Library/01-Summaries/` | `02-Library/02-Concepts/`
- **产出层**：`03-Output/01-灵感/` | `03-Output/02-选题池/` | `03-Output/04-已发布/`
- **操作日志**：`[[log.md]]`
- **系统配置**：`CLAUDE.md` | `SOUL.md` | `AGENTS.md`

---

*本索引由脚本自动维护，最后重建：{today}*
"""

with open(INDEX_PATH, 'w') as f:
    f.write(index_content)

print(f"✓ index.md rebuilt: {len(concepts)} concepts, {len(summaries)} summaries, {len(healths)} health reports")
