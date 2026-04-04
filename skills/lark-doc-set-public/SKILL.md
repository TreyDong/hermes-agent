---
name: lark-doc-set-public
version: 1.0.0
description: "设置飞书云文档为互联网公开（任何人无需登录即可查看）。当用户要求设置文档公开权限、让文档可被外部访问、设置互联网可见时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 文档设置互联网公开

> **前置条件：** 先阅读 [`lark-shared`](../lark-shared/SKILL.md) 了解认证与身份规则。

## 命令

```bash
lark-cli api PATCH "/drive/v1/permissions/${DOC_ID}/public" \
  --params '{"type":"docx"}' \
  --data '{
    "public": "anyone_with_link",
    "security_entity": "anyone_can_view",
    "link_share_entity": "anyone_readable",
    "invite_external": true
  }' --as user
```

**参数说明**：

| 字段 | 值 | 含义 |
|------|-----|------|
| `${DOC_ID}` | 文档 token | 从文档 URL 提取，如 `https://www.feishu.cn/docx/doxcnXXXX` 中的 `doxcnXXXX` |
| `type` | `docx` | 文档类型，固定为 `docx` |

**四个字段必须同时传入，缺一不可**：

- `public: "anyone_with_link"` — 启用链接分享
- `security_entity: "anyone_can_view"` — 任何人可查看（无需登录）
- `link_share_entity: "anyone_readable"` — 链接分享范围为所有人可读
- `invite_external: true` — 允许给外部人员发邀请

## 验证设置结果

```bash
lark-cli api GET "/drive/v1/permissions/${DOC_ID}/public" \
  --params '{"type":"docx"}' --as user
```

检查返回字段：

- `external_access: true` — 互联网外部可访问 ✅
- `share_entity: "anyone"` — 任何人可访问 ✅
- `link_share_entity: "anyone_readable"` — 链接可读 ✅

## 权限

| 操作 | 所需 scope |
|------|-----------|
| 查询/设置公开权限 | `drive:drive` |

若 token 缺少此 scope，重新授权：

```bash
lark-cli auth login --scope "drive:drive"
```

## 使用场景

**直接设置公开**：

用户给出文档链接或 doc_id，要求设置互联网公开。

**创建后立即公开**（两步合并）：

```bash
# Step 1: 创建文档
DOC_RESULT=$(lark-cli docs +create --title "标题" --markdown "## 内容")

# Step 2: 设置互联网公开（用 Step 1 返回的 doc_id）
DOC_ID="<上一步返回的 doc_id>"
lark-cli api PATCH "/drive/v1/permissions/${DOC_ID}/public" \
  --params '{"type":"docx"}' \
  --data '{"public":"anyone_with_link","security_entity":"anyone_can_view","link_share_entity":"anyone_readable","invite_external":true}' \
  --as user
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `99991679 Permission denied` | token 缺少 `drive:drive` scope | `lark-cli auth login --scope "drive:drive"` 重新授权 |
| `1063001 Invalid parameter` | `type` 未传或 `doc_id` 与 `type` 不匹配 | 确认文档是新版 docx 类型，`type` 参数值为 `docx` |
