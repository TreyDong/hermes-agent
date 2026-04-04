---
name: opencli-mac-remote
description: 在 NAS 上通过 SSH 远程操控 Mac 上的 opencli + Chrome 浏览器。Mac 安装 opencli + Browser Bridge 扩展，Chrome 有登录态，NAS 通过 Tailscale 直连 Mac 执行 opencli 命令。
category: devops
---

# OpenCLI Mac 远程操控

通过 SSH 在 NAS 上远程控制 Mac 的 Chrome 浏览器，执行 opencli 命令操作需要登录态的网站。

## 架构

```
NAS (Hermes/Hermes) → SSH (Tailscale) → Mac (opencli + Chrome + Browser Bridge)
```

## 前置条件

### Mac 上已安装
- opencli: `brew install opencli` 或 `npm install -g @jackwener/opencli`
- opencli Browser Bridge 扩展（通过 `opencli doctor` 提示安装）
- Chrome 已在运行

### Mac 用户名和密码
- 用户名: `xiaojigongzuoshi`
- 密码: `0112`
- Tailscale 域名: `macbook-air.tailda5466.ts.net`

## 关键文件路径

- Chrome profile: `/Users/Treydong/Library/Application Support/Google/Chrome`
- opencli 安装路径: `/opt/homebrew/bin/opencli`
- 扩展下载: `https://github.com/jackwener/opencli/releases/latest/download/opencli-extension.zip`

## 常用命令

### 检查状态
```bash
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli doctor'
```

### 操作浏览器（operate 模式）
```bash
# 打开网页
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate open https://example.com'

# 查看页面元素
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate state'

# 点击元素
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate click 3'

# 输入文字
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate type 5 "hello"'

# 截图
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate screenshot'
```

### 网站命令（无需浏览器）
```bash
# 小红书搜索
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli xiaohongshu search "关键词"'

# B站热门
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli bilibili hot --limit 5'

# Twitter
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli twitter timeline --limit 3'
```

### 链式操作（减少 SSH 连接开销）
```bash
sshpass -p '0112' ssh -o StrictHostKeyChecking=no xiaojigongzuoshi@macbook-air.tailda5466.ts.net 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate open https://www.baidu.com && opencli operate type 87 "测试" && opencli operate click 90 && opencli operate wait time 2 && opencli operate state'
```

## Chrome 进程管理

### 启动 Chrome（Mac 终端手动执行）
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

### 安装/更新扩展
```bash
# 下载扩展
curl -sL -o /tmp/opencli-extension.zip "https://github.com/jackwener/opencli/releases/latest/download/opencli-extension.zip"
unzip -o /tmp/opencli-extension.zip -d /tmp/opencli-extension

# 打开扩展页面（手动 Load unpacked）
open /tmp/opencli-extension
```

### 清理 Chrome 进程和锁文件
```bash
pkill -9 -f "Chrome" 2>/dev/null
rm -f "/Users/Treydong/Library/Application Support/Google/Chrome/SingletonLock"
rm -f "/Users/Treydong/Library/Application Support/Google/Chrome/SingletonCookie"
rm -f "/Users/Treydong/Library/Application Support/Google/Chrome/SingletonSocket"
```

## 常见问题

### "Extension: disconnected"
扩展未安装或未启用。按上述步骤重新安装 Browser Bridge 扩展。

### "Browser not connected"
Chrome 未启动或 opencli daemon 未运行。检查 `opencli doctor`。

### SSH 连接失败
确认 Mac 开启远程登录（系统设置 → 通用 → 共享 → 远程登录）。

### Google 账号被登出
不要用不同用户身份 SSH 进 Mac 后操作 Treydong 的 Chrome profile，会触发 singleton 冲突导致 session 损坏。
