# 浏览器操作代码片段（Subagent 直接调用）

## 1. Playwright 无头截图

```python
# 安装（仅首次）
import subprocess
subprocess.run(["python3", "-m", "playwright", "install", "chromium"], check=True)

# 截图
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com", timeout=15000)
    page.wait_for_load_state("networkidle")
    page.screenshot(path="/tmp/result.png", full_page=True)
    browser.close()
```

## 2. Playwright 滚动 + 提取内容

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(url, timeout=15000)
    page.wait_for_load_state("networkidle")
    
    # 滚动加载更多内容
    for _ in range(3):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1500)
    
    content = page.content()  # 完整 HTML
    text = page.inner_text("body")  # 纯文本
    browser.close()
```

## 3. curl_cffi（轻量请求）

```python
from curl_cffi import requests

# 基础请求
r = requests.get(url, impersonate="chrome")
print(r.text)

# 带参数
r = requests.post(url, json={"query": "xxx"}, impersonate="chrome")
```

## 4. OpenCLI Mac operate（最终兜底）

```bash
# Mac 上操作，需先确认 opencli operate 可用
opencli operate "帮我打开 Chrome，访问 https://example.com，然后截图"
```

## 5. Web Extract（简单页面，无需浏览器）

```bash
# 通过 hermes_tools 或直接 curl
curl -sL "$url" | python3 -c "
import sys, re
html = sys.stdin.read()
# 简单提取 title 和文本
title = re.search(r'<title>(.*?)</title>', html)
print('Title:', title.group(1) if title else 'N/A')
"
```

## 工具选择决策树

```
需要浏览器吗？
├── 公开页面，静态内容 → curl / web_extract
├── 需要 JS 渲染 → playwright screenshot
├── 被反爬拦截 → playwright + curl_cffi 组合
├── 需要登录态 / 复杂交互 → opencli mac operate
└── 全部失败 → opencli mac operate 兜底
```
