---
name: github-pr-from-issue
description: 从 GitHub Issue URL 直接创建 PR 的工作流。触发条件：用户发来 issue URL 并要求提交 PR。
---

# GitHub PR from Issue — 通用工作流

## 触发条件
用户发来 GitHub Issue URL，要求提交 PR。

## 工作流（4步）

### 1. 读取 Issue 页面
用 curl 抓取 issue 正文，提取问题描述：
```bash
# 提取 issue 标题和正文
curl -s "https://api.github.com/repos/{owner}/{repo}/issues/{num}" | jq '{title, body}'
```

### 2. 分析代码 + 找修复点
克隆仓库（如果需要），用 grep 定位硬编码值、错误逻辑：
```bash
git clone https://github.com/{owner}/{repo}.git /tmp/{repo}
cd /tmp/{repo}
# 找关键代码
grep -rn "problematic_code" .
```

### 3. 创建分支 + 改代码
```bash
cd /tmp/{repo}
git checkout -b fix/{issue-number}-{short-desc}
# 修改文件...
git add .
git commit -m "fix #${issue_number}: ${short_description}"
```

### 4. 推送到 fork 并创建 PR
```bash
# 如果没有 fork，先 fork（通过 GitHub CLI）
gh auth login  # 确保已认证
gh repo fork {owner}/{repo} --clone

# 推送分支
git push -u origin fix/{issue-number}-{short-desc}

# 创建 PR，自动关联 issue
gh pr create --title "fix #${issue_number}: ${title}" --body "Fixes #${issue_number}" --base main
```

## 关键经验
- **先 fork 再改**：不要直接在原仓库创分支，用 `gh repo fork`
- **PR body 写 `Fixes #XXX`**：自动关联并关闭 issue
- **一个 PR 只做一件事**：如果需要多改文件，确保改动都服务于同一个 issue
- **小改动先沟通**：如果 issue 比较开放（feature request），先问用户确认方向再动手

## 案例记录
- 2026-04-01：honcho #463 — 6行改动，将 `embedding_client.py` 和 `models.py` 中的硬编码 `1536` 替换为 `settings.VECTOR_STORE.DIMENSIONS`，向后兼容（默认仍是1536）。PR: #469。
