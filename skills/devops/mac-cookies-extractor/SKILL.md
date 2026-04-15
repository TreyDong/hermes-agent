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

### 3. Twitter tokens 优先用 browser-cookie3（推荐）
**关键**：Mac Chrome 的 Twitter 登录态 cookie 实际绑在 `.x.com` 域名，不是 `.twitter.com`。
必须指定 `domain_name='.x.com'` 才能读到 `auth_token` 和 `ct0`：

```bash
# 1. 解锁 Mac Keychain
ssh Mac主机 "security unlock-keychain -p '密码' ~/Library/Keychains/login.keychain-db"

# 2. 用 uv + browser-cookie3 读 .x.com domain（不是 .twitter.com！）
ssh Mac主机 "HOME=/Users/Treydong ~/.local/bin/uv run --with browser-cookie3 python3 -c \"
import browser_cookie3, json
cookies = browser_cookie3.chrome(domain_name='.x.com')  # 关键：不是 .twitter.com
for c in cookies:
    if c.name in ['auth_token','ct0']:
        print(c.name + '=' + c.value)
\""

# 3. 拿到 token 后在 NAS 上设置环境变量
export TWITTER_AUTH_TOKEN=<auth_token值>
export TWITTER_CT0=<ct0值>
twitter status  # 验证
```

**为什么之前失败**：browser_cookie3 默认读不到 Twitter Cookies，因为 Twitter 把关键 Cookie（auth_token, ct0, twid）存在 `.x.com` 而非 `.twitter.com`——用 `.twitter.com` 只能读到 guest_id 类公开 Cookie。

**Mac 上 uv 路径**：Mac 的 uv 在 `~/.local/bin/uv`，不是全局 `uv`，SSH 到 Mac 时需要用完整路径或 `HOME=/Users/Treydong ~/.local/bin/uv`。

### 3.1 token 传输：禁止用管道直接 pipe（会超时/被截断）

Mac → NAS 传 token 时，直接 `ssh ... | python3` 或 `ssh ... > file` 会被阻塞，必须用以下方式之一：

**方式A（推荐）：scp 文件中转**
```bash
# Mac 写文件
ssh Mac主机 "HOME=/Users/Treydong ~/.local/bin/uv run --with browser-cookie3 python3 -c '
import browser_cookie3
for c in browser_cookie3.chrome(domain_name=\".x.com\"):
    if c.name == \"auth_token\": open(\"/tmp/twitter_auth_token.txt\",\"w\").write(c.value)
    if c.name == \"ct0\": open(\"/tmp/twitter_ct0.txt\",\"w\").write(c.value)
'"
# scp 拷回
scp Mac主机:/tmp/twitter_auth_token.txt /tmp/
scp Mac主机:/tmp/twitter_ct0.txt /tmp/
# NAS 写入 .env
echo "TWITTER_AUTH_TOKEN=$(cat /tmp/twitter_auth_token.txt)" >> ~/.hermes/.env
echo "TWITTER_CT0=$(cat /tmp/twitter_ct0.txt)" >> ~/.hermes/.env
```

**方式B：进程替换 `<(...)` 避免管道阻塞**
```bash
python3 -c "import sys,json; ..." < <(ssh Mac主机 "cat ~/.xhs-cli/cookies.json") > /tmp/xhs.json
```

**方式C：分步骤 echo（适用于短字符串如 auth_token）**
```bash
AUTH_TOKEN=$(ssh Mac "cat /tmp/twitter_auth_token.txt" | tr -d '\n')
```

### 3.2 twitter-cli token 写入验证
```bash
source ~/.hermes/.env
twitter status  # 必须返回 authenticated: true
```

## XHS Cookies 迁移（xhs-cli）

**Mac 存哪**：`~/.xhs-cli/cookies.json`

```bash
# 方式A：scp
scp Mac主机:/Users/Treydong/.xhs-cli/cookies.json ~/.xhs-cli/cookies.json

# 方式B：进程替换
python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False))" \
  < <(ssh Mac主机 "HOME=/Users/Treydong cat ~/.xhs-cli/cookies.json") \
  > ~/.xhs-cli/cookies.json

# 验证
xhs status
```

**坑**：NAS 上 xhs-cli 版本可能较旧（`xhs-cli 0.1.4`），Mac 是 `0.6.4`，但只要 cookies 格式兼容就能用，`xhs status` 通过即可。

## Reddit Cookies 迁移（rdt-cli）

**Mac 存哪**：`~/.config/rdt-cli/credential.json`

```bash
# scp 拷贝（credential.json 较大，用 ssh 命令行会超时）
scp -o StrictHostKeyChecking=no Mac主机:/Users/Treydong/.config/rdt-cli/credential.json /tmp/rdt_creds.json

# 进程替换方式（只取关键字段）
python3 -c "
import json, sys
d = json.load(sys.stdin)
# 只保留关键 cookies 字段
key_fields = ['reddit_session', 'token_v2', 'loid', 'edgebucket', 'modhash']
cookies = {k: v for k, v in d.get('cookies', {}).items() if k in key_fields}
print(json.dumps({'cookies': cookies, 'saved_at': d.get('saved_at')}, ensure_ascii=False))
" < <(ssh Mac主机 "HOME=/Users/Treydong cat ~/.config/rdt-cli/credential.json") > /tmp/rdt_creds.json

# 写入 NAS
mkdir -p ~/.config/rdt-cli
cp /tmp/rdt_creds.json ~/.config/rdt-cli/credential.json

# 验证
rdt status
```

## 验证
- Reddit: `rdt status`
- Twitter: `twitter status`
- XHS: `xhs status`

## 坑
- Keychain 不解锁 → browser-cookie3 返回空（只返回 guest_id）
- **Mac Chrome cookies 在 `.x.com` 不是 `.twitter.com`** → 必须用 domain_name='.x.com'
- SSH 管道直接 pipe 会超时/截断 → 用 scp 或 `<(...)` 进程替换
- Mac 上 `uv` 路径是 `~/.local/bin/uv`，不是系统 `uv`
