---
name: ark-api-debug
description: 火山方舟 ARK API 调试技巧 — 模型开通检测、网络问题定位、已知坑点
triggers:
  - ARK API ModelNotOpen
  - 火山方舟视频生成失败
  - doubao-seedance 权限问题
---

# ark-api-debug

火山方舟 ARK API 调试的实战经验。

## 快速检测：账号能访问哪些模型

```bash
source ~/.hermes/.env
curl -s --max-time 20 -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks?page_size=20" \
  -H "Authorization: Bearer $ARK_API_KEY"
```
能返回200说明API Key有效，且可以从中看到账号**历史上成功使用过的模型ID**（如 `doubao-seedance-1-5-pro-251215`）。

## ModelNotOpen 的真正含义

**症状：** POST 创建视频任务返回 `ModelNotOpen`，但 GET 能读到历史任务。

**原因：** 模型服务临时不可用（平台端问题），不代表账号真的没权限开通。

**解决步骤：**
1. 去火山引擎控制台（ark.console.volces.com）确认模型已开通
2. 尝试不同 region endpoint：
   - `https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks`
   - `https://ark.cn-shanghai.volces.com/api/v3/contents/generations/tasks`
3. 确认是服务问题还是账号问题

## 网络环境坑点

### execute_code sandbox vs terminal 网络隔离（重要！）

**现象：** 在 Banana 服务器上：
- terminal 直接执行 `curl` → ARK API 完全正常（GET/POST都通）
- execute_code 的 Python sandbox → 某些 API 不通或返回奇怪错误（如 401/403）

**教训：** 调试 ARK API 时**优先用 terminal 执行 curl**，不要在 execute_code 里调 `urllib`。两者网络环境不同。

### API Key 获取路径

Banana 服务器的 ARK_API_KEY 在 `~/.hermes/.env`：
```bash
source ~/.hermes/.env && echo $ARK_API_KEY
```

## 已知可用的模型（2026-04-12）

| 模型 ID | 状态 | 备注 |
|---------|------|------|
| doubao-seedance-1-5-pro-251215 | 历史成功（当前服务中断） | 能GET到15条历史任务，POST创建报ModelNotOpen |
| doubao-seedance-2-0-260128 | 未激活 | ModelNotOpen |

## 标准调试流程

1. terminal 查历史任务 `GET /api/v3/contents/generations/tasks`
2. 从历史任务里确认模型是否在账号中可用
3. 用 curl 直接 POST 创建任务测试（不加 python sandbox）
4. 若 POST 报 ModelNotOpen → 去控制台确认开通状态
5. 若所有 region 都失败 → 检查是否是 IP/网络限制

## 视频生成任务创建示例（已知可用格式）

```bash
source ~/.hermes/.env
curl -s --max-time 30 -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [{"type": "text", "text": "你的提示词"}],
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 10,
    "generate_audio": true,
    "watermark": false
  }'
```
