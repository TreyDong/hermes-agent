---
name: course-planning-from-lark-doc
version: 1.0.0
description: 从飞书文档规划内训课程的工作流：读取飞书文档 → 理解客户业务 → 重构课程内容适配本地 OpenClaw。用于企业 AI 内训课程设计场景。
triggers:
  - 发来飞书文档链接让规划课程
  - 基于文档最后部分重新设计课程
  - 客户需要本地 OpenClaw 而非云端产品
---

# 课程规划工作流

## 标准流程

### Step 1：读取飞书文档
```bash
# 云文档（非 wiki）
lark-cli docs +fetch --doc <document_token> --format pretty

# 如果是 wiki 链接，先查真实 token
lark-cli wiki spaces get_node --params '{"token":"<wiki_token>"}'
```

### Step 2：识别客户业务
- 网站 → 用 opencli operate 打开并截图
- 搜索 + 提取内容辅助理解业务范围

### Step 3：确认课程定位
关键决策点（每次都要问清楚）：
1. 昨天/之前讲了什么 → 今天接续什么
2. 云端产品 vs 本地 OpenClaw → 核心差异是什么
3. 用户最希望突出的重点是什么
4. 动手练习 vs 纯演示

### Step 4：两节课重构模板

当文档是「通用版六节课」需要适配「本地 OpenClaw + 特定客户场景」时：

```
第一节（90分钟）：本地核心能力 × 客户场景Demo
  - 回扣昨天云端认知，建立本地为什么更强的逻辑
  - 2-3个核心Demo（纯演示为主）
  - Skill设计方法论（重点环节）
  - Q&A

第二节（90分钟）：具体BU场景全流程实战
  - 痛点回顾
  - 3-4个Demo串成完整业务流
  - 讨论 + 场景规划
```

### Step 5：交付给用户的格式
- 课程背景变化说明
- 两节课模块表格（含时长）
- Demo 清单
- 底层逻辑主线
- 确认下一步（打磨哪个Demo/确认学员范围）
