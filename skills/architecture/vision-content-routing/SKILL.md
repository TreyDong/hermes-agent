---
name: vision-content-routing
description: Vision内容路由——模型原生视觉 vs 工具预分析的正确路由方式
category: architecture
---
# Vision Content Routing — Native vs Tool-based

## 核心原则
模型有原生视觉能力 → 直接把图片原始数据（base64 data URL）塞进上下文 → 模型自己看  
模型无视觉能力 → 才走 `vision_analyze` 预分析成文字描述

## 当前问题
Gateway 统一走 `_enrich_message_with_vision()` 预分析+文字注入，图片原始数据不进模型 context。

## 相关 PR
- **PR #4535** (OPEN+CONFLICTING)：feat(multimodal): native image content flow across gateway, agent, read_file
  - 在 `agent/model_metadata.py` 加 `supports_vision` 判断
  - 在 `gateway/run.py` 按模型能力路由
  - 状态：DIRTY+CONFLICTING，0 comments，无 review，无合入计划
  - 本地代码（`~/.hermes/hermes-agent/`）未合并此 PR

## 工具链（容易搞混）
| 工具 | 路径 | 依赖 |
|------|------|------|
| `vision_analyze_tool` (tools/vision_tools.py) | 读本地文件→base64→LLM | 无外部依赖 |
| `browser_vision` (tools/browser_tool.py) | Camofox 浏览器截图 | Camofox 服务 localhost:9377 |
| `mcp_browser_vision` | 封装 browser_vision | Camofox REST API |
| `mcp_MiniMax_understand_image` | MiniMax 图像理解 API | MiniMax MCP |

## 故障排查
- "图片加载失败 404" → Camofox 服务没运行，不是图片文件问题
- 本地图片路径对模型是黑屏 → 必须通过工具调用访问
- FLUX 图像生成挂 → FalClientHTTPError，应换 MiniMax 原生图像生成而非 HTML 渲染兜底
