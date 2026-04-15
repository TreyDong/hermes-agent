---
name: browser-subagent
description: 浏览器任务自动委托——检测到网页操作时自动 spawn subagent，避免污染主会话上下文。触发：网页操作、截图、爬取、登录态操作
---

# Browser Subagent 自动委托

## 核心逻辑

检测到需要浏览器操作时，**不直接在主会话执行**，自动 spawn subagent 处理，最后把结果摘要接回主会话。

## 工具链优先级

```
1. curl_cffi（轻量，默认首选）—— 纯 HTTP，impersonate 浏览器指纹，被拦截再换
2. playwright（重量兜底）—— JS 渲染/滚动/交互
3. opencli mac operate（最终兜底）—— 需要 Mac 登录态时
```

## 自动判断规则

| 任务类型 | 推荐工具 |
|---------|---------|
| 公开网页、无反爬 | 无头浏览器 |
| 有 JS 渲染、风控检测 | camuflage |
| 需要登录态（Cookie/Session）| opencli Mac |
| 简单内容提取 | 无头 + web_extract |
| 复杂交互操作 | opencli Mac |

## 使用方式

在主会话中说「帮我查 XXX」「去网页看看」「操作一下 XXX」，直接触发本 skill 自动委托。

也可以显式调用：

```
/browser-subagent "任务描述"
```

## Subagent Prompt 模板

```
你是浏览器操作专家。任务：{task}

可用工具（按优先级，从轻量到重量）：
1. curl_cffi（最轻量，默认首选）—— 纯 HTTP 请求，不开浏览器
2. playwright screenshot（重量兜底）—— JS 渲染、滚动、交互
3. opencli mac operate（最终兜底）—— 需要 Mac 登录态时
4. web_extract（极简页面）—— 直接 curl 抓正文

操作顺序：
- 公开页面：先试 curl_cffi，最快
- curl_cffi 被拦截（403/Cloudflare/JS 检测）：playwright screenshot
- playwright 也被检测：curl_cffi --impersonate="chrome" 重试
- 需要登录态：opencli mac operate
- 全部失败：opencli mac operate 最终兜底

结果格式：
- 成功：关键信息摘要（≤500字）+ 相关链接列表
- 失败：尝试了哪些方法 + 失败原因

输出限制：只返回摘要，不返回完整 HTML 或页面内容。
```

## 验证步骤

完成后确认 subagent 返回了有效结果，结果已注入主会话。
