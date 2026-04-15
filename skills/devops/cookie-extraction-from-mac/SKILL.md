---
name: cookie-extraction-from-mac
description: 从 Mac Chrome 提取 Twitter/XHS/RDT cookies 到 NAS CLI 工具
category: devops
---

# 从 Mac Chrome 提取 Cookies 到 NAS

## 核心问题
Mac Chrome 的 Twitter/X 登录态 cookie 存在 `.x.com` domain，不是 `.twitter.com`。browser_cookie3 默认 domain 参数读出来是空的。

## 关键发现
- Mac Chrome remote-debug 新 profile 命令：
  ```bash
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/Users/xiaojigongzuoshi/Library/Application\ Support/Google/Chrome/ChatApp
  ```
- SSH tunnel：`ssh -L 9223:localhost:9222 xiaojigongzuoshi@192.168.31.108`
- **Cookie domain 关键**：Twitter 登录态在 `.x.com`，browser_cookie3 读时要指定 `domain='.x.com'`
- Keychain 解锁：`security unlock-keychain -p '0112' /Users/xiaojigongzuoshi/Library/Keychains/login.keychain-db`

## Twitter token 提取流程
1. SSH 到 Mac，解锁 keychain：`security unlock-keychain -p '0112'`
2. 用 twitter-cli token（Mac 已装 v1.6.1 via uv）：`source ~/.zshrc && twitter-cli token`
3. 若失败，用 browser_cookie3 读取：
   ```python
   import browser_cookie3
   cj = browser_cookie3.chrome(cookie_file=None, domain='.x.com')
   for c in cj:
     if 'auth_token' in c.name or 'ct0' in c.name:
       print(c.name, c.value)
   ```
4. 用文件传输避免 token 截断：
   ```bash
   # Mac 上保存到文件
   python3 -c "import browser_cookie3; ..." > /tmp/twitter_tokens.txt
   
   # NAS 上读取
   sshpass -p '0112' ssh xiaojigongzuoshi@192.168.31.108 "cat /tmp/twitter_tokens.txt"
   ```

## xhs-cli v0.6.4 (Mac) → NAS
- Mac cookie 路径：`~/.xhs-cli/cookies.json`
- NAS cookie 路径：`~/.xhs-cli/cookies.json`
- 直接 scp 覆盖：Mac 版本太老(0.1.4)，pip 源没有新版，直接拷整个 xhs-cli 目录比升级更可靠

## rdt-cli
- Mac credential 路径：`~/.config/rdt-cli/credential.json`
- NAS credential 路径：`~/.config/rdt-cli/credential.json`
- 直接 scp 覆盖

## 验证命令
```bash
# Twitter
source ~/.hermes/.env && twitter status

# XHS
xhs-cli status

# RDT
rdt-cli status
```
