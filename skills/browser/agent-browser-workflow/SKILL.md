---
name: agent-browser-workflow
description: 浏览器自动化工作流（Mac/NAS双端）
---

# agent-browser Workflow

## 触发条件
浏览器操作、网页截图、网页自动化测试

## 工具
- Mac：chrome-mcp-server（端口9222）+ agent-browser（端口9223）
- NAS（192.168.31.154）：agent-browser via SSH

## Mac 上 Chrome 启动
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```

## agent-browser 基本命令
```bash
agent-browser run                    # daemon 模式
agent-browser open "https://..."     # 新建标签打开URL
agent-browser snapshot               # 获取当前页面结构
agent-browser fill "#selector" "text"# 输入
agent-browser click "#selector"      # 点击
agent-browser screenshot /tmp/a.png # 截图
agent-browser eval "js"             # 执行JS
```

## NAS SSH 方式
```bash
sshpass -p '11114444' ssh banana@192.168.31.154 "agent-browser screenshot /dev/null"
```

## 清理残留进程
```bash
pkill -f agent-browser
```

## NAS agent-browser 安装
```bash
npx skills add agent-browser -g -y
npm install -g agent-browser --prefix ~/.npm-global
```
