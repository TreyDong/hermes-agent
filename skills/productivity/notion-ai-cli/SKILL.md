---
name: notion-ai-cli
description: 通过 opencli 远程操控 Mac Chrome 浏览器操作 Notion AI 对话，提取回复内容总结给用户
category: productivity
---
# Notion AI CLI 操作

通过 opencli 远程操控 Mac Chrome 浏览器操作 Notion AI 对话。

## 环境
- Mac IP: `192.168.31.132`
- Mac 用户: `banana`，密码: `0112`
- opencli daemon 在 Mac 后台运行，端口 9222

## 已知问题
- Mac SSH 密码是 `0112`（之前有过错误记忆 `Mini1314.`，完全是幻觉，不要信）
- SSH 连接失败超过几次会被 fail2ban 拦，需要等 30 秒

## 完整流程

### 1. 打开 Notion AI 并选 Opus 模型
```bash
opencli navigate "https://www.notion.so/ai"
sleep 3
opencli operate click "text=Auto"
sleep 2
opencli operate click "text=Opus"
```

### 2. 发 prompt 并等待
```bash
opencli operate eval 'document.querySelector("[data-testid=\"notion-ai-input\"]")?.click()'
sleep 1
opencli operate eval 'document.querySelector("[data-testid=\"notion-ai-input\"] .leading-text")?.setAttribute("contenteditable", "true")'
opencli operate write "/tmp/prompt.txt" "你的prompt内容"
opencli operate eval 'navigator.clipboard.writeText(`$(cat /tmp/prompt.txt)`)'
opencli operate eval 'document.execCommand("paste")'
sleep 1
opencli operate click "text=Send"
```

### 3. 滚动提取 AI 回复
Notion AI 回复在 `div[data-testid="notion-ai-response"]` 里的 `.leading-text` 元素。
AI 处理时会显示 "Creating pages >" 等状态，处理完可能跳转到新页面。

### 4. 内容总结
用 `opencli operate eval` 提取文本后用 LLM 总结。不要截图——要提取文本内容。

## 注意事项
- 不要截图——要提取文本内容总结给用户
- 可能需要滚动页面
- Notion AI 无法直接截 Notion 内部图（AI 的限制）
