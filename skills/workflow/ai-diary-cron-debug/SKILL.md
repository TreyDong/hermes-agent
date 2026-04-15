---
name: ai-diary-cron-debug
description: AI日记cron连续"休息日"误报时的调试方法——session_search是FTS5全文检索不支持日期过滤，需用session文件扫描
triggers:
  - AI日记 cron 返回"今日无对话记录"
  - 连续多日休息日但用户明显有活动
  - cron job_id 为 669693e18570
---

# AI 日记 Cron 调试方法

## 触发条件
AI 日记 cron 任务连续多日返回"今日无对话记录，休息日"，但用户明显有活动。

## 根因（重要修正）

**`session_search` 是 FTS5 全文检索，搜的是消息内容里出现的词，不支持日期过滤。**

常见误解：
- ❌ `session_search(query="date:2026-04-15")` → 无结果（FTS 不识别 `date:` 语法）
- ❌ `session_search(query="2026-04-15")` → 只会在消息文本里搜索 "2026-04-15" 这个字符串
- ❌ 以为搜关键词能找到当天所有对话 → 实际只能搜到消息内容含该词的结果

Session 文件格式：`~/.hermes/sessions/YYYYMMDD_HHMMSS_*.jsonl`
- 文件名前缀就是日期（YYYYMMDD），例如 `20260415_071229_73754782.jsonl`
- 这是最可靠的日期定位方式，不依赖消息内容

## 调试步骤

### 第一步：检查 session 文件
```bash
ls -lt ~/.hermes/sessions/*${YYYYMMDD}*.jsonl
```
有文件 → 当天有会话；无文件 → 真的没有会话（休息日）

### 第二步：读 session 文件内容
```bash
cat ~/.hermes/sessions/20260415_*.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try:
        obj=json.loads(line)
        if isinstance(obj,dict) and obj.get('role')=='user':
            print('USER:', obj.get('content','')[:200])
    except: pass
"
```
提取所有 user 消息作为对话记录。

### 第三步：session_search 的正确用法
`session_search` 适合**按话题搜**（如搜 "飞书" "推特"），不适合按日期查。
搜出来的结果要结合文件时间戳判断是否是当天的。

## 正确方案：扫描 session 文件（2026-04-15 修复版）

Cron prompt 里的第一步从：
```
session_search 工具，搜索今天日期相关对话记录
```
改为：
```
terminal 执行 ls ~/.hermes/sessions/*${YYYYMMDD}*.jsonl 找到今日 session 文件
读取所有今日 .jsonl 文件，解析 user 消息
```

## 已知修复项（2026-04-15）
- ✅ 路径：`10-Base/01-Raw/01-Inbox/` → `90-Daily/`
- ✅ 搜索：session 文件扫描（文件名 YYYYMMDD 前缀）代替 session_search 关键词
- ✅ 移除 prompt 内 Discord 通知（delivery 机制自动推送）

## 已知持续问题
- Discord 投递由 cron delivery 机制处理，不依赖 discocli
- lark-cli 缺 scope（`calendar:calendar:read` 等）— 4/2 起未解决
