# Chengfeng Autopause Skill

## 这是什么

一个小红书千帆推广（chengfeng.xiaohongshu.com）的创意自动停投 Skill。

当发现创意满足停投条件（消耗 > X 元 且 成交 = 0）时，自动列出待停创意清单，等人类确认后执行暂停操作。

## 安装

### 前置依赖

1. **OpenClaw**（必须）
   - 安装方式：https://docs.openclaw.ai

2. **agent-browser CLI**（必须）
   - agent-browser 是浏览器自动化工具，OpenClaw 使用它控制 Chrome 完成页面操作
   - 如果 `which agent-browser` 找不到，从这里安装：
     ```bash
     npm install -g @openclaw/agent-browser
     ```

3. **Chrome CDP Session**（必须）
   - 千帆平台需要已登录的 Chrome 会话
   - 确保 Chrome 开启了 Remote Debugging Port（默认 9222）
   - Session 名必须是 `chengfeng`：
     ```bash
     # 方式1：使用已有 session
     agent-browser --session chengfeng status
     
     # 方式2：新建（需要人工扫码登录一次）
     agent-browser connect http://127.0.0.1:9222 --session chengfeng
     ```

4. **千帆账号已登录**（必须，人工操作一次）
   - 访问 https://chengfeng.xiaohongshu.com
   - 用短信验证码登录
   - 登录态会持久化到 Chrome Cookie，后续无需再登录

### 安装 Skill

把 `chengfeng-autopause` 目录放到 skills 目录：

```bash
# 找到你的 skills 目录（通常是 ~/.agents/skills/ 或 ~/.openclaw/skills/）
cp -r chengfeng-autopause ~/.agents/skills/

# 验证安装成功
ls ~/.agents/skills/chengfeng-autopause/
# 应该看到：SKILL.md  evals/
```

## 使用

### 触发方式

当用户提到以下内容时，这个 Skill 会自动激活：

- 「千帆推广」「乘风计划」「小红书投流」
- 「停投创意」「创意策略」「自动停投」
- 「谢老师」（客户的千帆账号）

### 标准使用流程

```
1. Agent 读取 Skill 说明
2. 连接 Chrome CDP（session: chengfeng）
3. 打开 https://chengfeng.xiaohongshu.com/cf/ad/manage
4. 用 JavaScript eval 读取创意数据
5. 按配置的规则筛选目标创意
6. 输出待确认列表
7. 等待人类说「确认」
8. 执行暂停操作
```

### 停投规则配置

用户在提示词里用自然语言配置停投标准，例如：

```
消耗超过10元且7天成交笔数为0的创意→停投
消耗超过50元且ROI低于0.5的创意→停投
```

Skill 会用 LLM 解析这条规则，生成筛选代码，在创意数据上执行。

### 关键数据字段

| 字段 | 含义 |
|-----|------|
| fee | 近7天消耗金额（元） |
| dealOrderNum7d | 7天支付成交笔数（已付款） |
| totalOrderNum7d | 7天下单笔数（含未付款） |
| dealGmv7d | 7天支付成交金额 |
| status | 创意状态（有效/暂停） |

**成交判断：** 默认用 `dealOrderNum7d`（已付款）。如果用户说「成交」但没明确，按已付款理解。

### 重要限制

- **必须人类确认后才能暂停**——Skill 只输出清单，不自动执行暂停
- **依赖已登录的 Chrome**——Cookie 过期后需要重新扫码登录
- **SMS 登录无法自动化**——首次设置需要人工操作

## 文件结构

```
chengfeng-autopause/
├── SKILL.md          # Skill 主体说明（Agent 读取此文件）
├── README.md         # 本文件
└── evals/           # 测试用例（可选）
```

## 故障排除

| 问题 | 解决方法 |
|-----|---------|
| 「Session not found」 | 用 `agent-browser --session chengfeng status` 确认 session 是否存在 |
| 「数据读不到」 | 先用 `agent-browser snapshot` 确认页面已完全加载 |
| 「下拉框点不开」 | 用 `dispatchEvent(new MouseEvent('click'))` 而不是 `click()` |
| 「Cookie 过期」 | 删除 Chrome 里 chengfeng.xiaohongshu.com 的 cookies，重新扫码登录 |
