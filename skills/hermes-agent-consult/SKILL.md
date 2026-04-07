---
name: hermes-agent-consult
description: "Consult hermes-agent docs before any modification or question about Hermes. Trigger: any question or modification request involving Hermes (gateway, CLI, tools, config, agent, etc.)."
category: hermes
---

# Hermes Agent 文档查询规范

## 触发条件

当用户请求以下任何操作时，必须先查询文档：
- 修改 Hermes 配置（config.yaml、.env、settings）
- 修改 Hermes Gateway（gateway/run.py、platforms、webhooks）
- 修改 Hermes CLI（hermes_cli/、commands、slash commands）
- 修改 Hermes Agent（run_agent.py、model_tools.py、agent/）
- 修改 Hermes Tools（tools/registry.py、toolsets.py）
- 修改 Skills 系统（skill_commands.py、skills hub）
- 修改 Cron 调度（cron/）
- 回答关于 Hermes 架构、原理、命令的问题
- 修改 ACP 适配器（acp_adapter/）

## 查询步骤

### 1. 读取 AGENTS.md（主文档）
路径：`/home/banana/.hermes/hermes-agent/AGENTS.md`

这是最核心的文档，包含了完整的项目结构、架构说明、工具注册规范、CLI 规范、配置文件格式等。

### 2. 读取 docs/ 目录下的相关文档
路径：`/home/banana/.hermes/hermes-agent/docs/`

可能包含：ACP setup、honcho integration、migration guide、plans 等。

### 3. 读取相关源码文件（如有必要）
如果文档不足以回答，再查看具体源码文件。

## 核心原则

- **不得在没有阅读文档的情况下修改 Hermes 相关文件**
- **不得凭记忆或类推回答 Hermes 架构问题**
- **配置文件修改前必须确认当前值**
- **修改前必须确认修改后会不会影响其他组件**
- **涉及 API、结构、命令规范的答案必须从文档中找依据**

## 常见文档路径速查

| 需求 | 文档路径 |
|------|---------|
| 项目结构、工具注册、CLI规范 | `/home/banana/.hermes/hermes-agent/AGENTS.md` |
| ACP 配置 | `/home/banana/.hermes/hermes-agent/docs/acp-setup.md` |
| Honcho集成 | `/home/banana/.hermes/hermes-agent/docs/honcho-integration-spec.md` |
| Gateway架构 | `/home/banana/.hermes/hermes-agent/gateway/run.py`（配合AGENTS.md） |
| 工具实现 | `/home/banana/.hermes/hermes-agent/tools/registry.py`（配合AGENTS.md） |
