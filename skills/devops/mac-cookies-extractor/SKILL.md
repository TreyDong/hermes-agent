---
name: mac-cookies-extractor
description: 从 Mac Chrome 提取浏览器 cookies 供 NAS CLI 使用
trigger: Mac Chrome cookies / reddit twitter 登录态迁移 / keychain 解锁
---
# Mac Cookies 提取工作流

从 Mac Chrome 提取浏览器 cookies 供 NAS 上的 CLI 工具使用。

## 适用场景
Reddit、Twitter 等已登录 Mac Chrome，但需要在 NAS CLI 上复现登录态。

## 依赖
- Mac 上安装了 `opencli` 和 Chrome Remote Debugging (9222)
- NAS 上有 `browser-cookie3` (`pip install browser-cookie3`)

## 步骤

### 1. 解锁 Mac Keychain
```bash
ssh Mac主机 "security unlock-keychain -p 密码 ~/Library/Keychains/login.keychain-db"
```

### 2. 尝试 browser-cookie3（适用于 Reddit）
```bash
ssh Mac主机 "python3 -c \"
import browser_cookie3
import json
cookies = browser_cookie3.chrome(domain_name='.reddit.com')
for c in cookies:
    print(f'{c.name}={c.value}')
\""
```
输出示例：`reddit_session=...; ...`

### 3. Twitter tokens 优先用 twitter-cli 自带命令
twitter-cli 用 `twitter-cli token` 直接读取 Mac 上存储的 token（比抓 cookie 更完整）：
```bash
ssh Mac主机 "twitter-cli token"
```
输出 `auth_token=xxx` 和 `ct0=xxx`。

### 4. CDP 备选方案（Mac Chrome 9222）
```bash
# 先确认端口
ssh Mac主机 "lsof -i :9222 | head"

# 若有标签页打开，可直接用 opencli operate 注入JS
opencli operate exec --session-id <id> "document.cookie"
```

**注意**：Mac Chrome 9222 可能走的是独立 profile（如 gemini），不是用户默认 profile，此时 cookies 不在那里。

## 验证
- Reddit: `rdt-cli me`
- Twitter: `twitter-cli user treydtw`

## 坑
- Keychain 不解锁 → browser-cookie3 返回空
- Mac Chrome 9222 profile 与用户 profile 不同 → cookies 不在
