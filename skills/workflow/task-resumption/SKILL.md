---
name: task-resumption
description: When user says "继续" without specifying what — recover context from sessions and task files
---
# Task Resumption

When the user says "继续这个任务" (continue this task) or similar without specifying what task, recover the context from session history before proceeding.

## Recovery Steps

1. **session_search** with the task keywords from the task file name/content
2. Look in `/vol1/1000/知识库/01-Tasks/` for the relevant task markdown file — it contains `discordThreadUrl` with the Discord thread ID
3. Search sessions for that thread ID: `grep -l "<thread_id>" ~/.hermes/sessions/20260*.jsonl`
4. Read the most recent matching session — the last 50-100 lines of the JSONL give you current state
5. Check the task file itself for status: `status: open/in-progress/done`

## What to Recover

- What was being worked on (the actual task, not just the most recent subtask)
- What was left undone or undecided
- Current state of any scripts/workflows being built
- What the user's next step options are

## Important

The session most recently referenced by the task file may NOT be today's session — the active conversation could be in an earlier session. Always grep by thread ID to find ALL relevant sessions, then read the most recent one.

## Output

Start with a brief summary of what you found: "Session 背景：上次主要在修X，任务Y本身还没动，待办是A/B/C。从哪里继续？"
