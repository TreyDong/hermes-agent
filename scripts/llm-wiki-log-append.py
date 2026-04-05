#!/usr/bin/env python3
"""
LLM Wiki Log Append Script
Appends an entry to log.md without modifying existing content.

Usage:
  python3 ~/.hermes/scripts/llm-wiki-log-append.py ingest "karpathy/llm-wiki.md" "处理3篇新raw，新增摘要3条，新增概念1个"
  python3 ~/.hermes/scripts/llm-wiki-log-append.py lint "" "发现2个孤立概念，已修正1个链接"
"""

import sys
import os
from datetime import datetime

LOG_PATH = "/vol1/1000/知识库/10-Base/02-Library/log.md"

if len(sys.argv) < 3:
    print("Usage: log-append.py <type> <title> <description>")
    sys.exit(1)

op_type = sys.argv[1]   # ingest | lint | compile | custom
title = sys.argv[2]     # e.g. "karpathy/llm-wiki.md"
desc = sys.argv[3] if len(sys.argv) > 3 else ""  # e.g. "处理3篇新raw"

now = datetime.now().strftime("%Y-%m-%d %H:%M")
today_date = datetime.now().strftime("%Y-%m-%d")

entry = f"\n## [{today_date}] {op_type} | {title}\n"
if desc:
    entry += f"- 操作：{desc}\n"

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, 'a') as f:
        f.write(entry)
else:
    # Create with header if doesn't exist
    header = f"""---
title: 知识库操作日志
description: LLM Wiki 知识库操作时间线
created: {today_date}
---

# 知识库操作日志

> 本文件是知识库的时间线记录。每次 ingest、query、lint、compile 操作都追加记录于此。
> 格式：`grep "^## \\[" log.md | tail -N` 查看最近 N 条操作

"""
    with open(LOG_PATH, 'w') as f:
        f.write(header + entry)

print(f"✓ log entry appended: [{today_date}] {op_type} | {title}")
