---
name: xhs-cli-qr-login-image
description: xhs cli QR 登录生成图片——从 camoufox 拦截 QR URL 并用 qrcode 库生成 PNG 图片，用于非终端环境（Discord/飞书）扫码认证
triggers:
  - xhs login
  - 小红书 QR 登录
  - xhs cli 二维码
---

# xhs-cli QR 登录生成图片

## 背景

xhs cli 的 `xhs login --qrcode` 在终端渲染 QR 为 ASCII 艺术（`▀▄█` 字符拼图），无法在 Discord 等平台分享。  
需要从浏览器流量中截取真实 QR URL，生成 PNG 图片发给用户扫码。

## 核心原理

xhs cli 使用 camoufox 无头浏览器打开小红书登录页，拦截 POST `/api/sns/web/v1/login/qrcode/create` 响应，从 JSON body 中提取 `data.url` 即为可扫码的 QR 链接。

## 标准流程

### 1. 安装依赖

```bash
pip install qrcode pillow --break-system-packages -q
```

### 2. 获取 QR URL 并生成图片

```python
import sys
sys.path.insert(0, '/home/banana/.local/share/uv/tools/xhs-cli/lib/python3.11/site-packages')

from camoufox.sync_api import Camoufox
import qrcode

QR_CREATE_ENDPOINT = "/api/sns/web/v1/login/qrcode/create"
LOGIN_URL = "https://www.xiaohongshu.com/login"

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    
    with page.expect_response(
        lambda r: QR_CREATE_ENDPOINT in r.url and r.request.method == "POST",
        timeout=20_000
    ) as resp_info:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20_000)
    
    data = resp_info.value.json()
    qr_url = data.get("data", {}).get("url") or data.get("url", "")
    
    qr = qrcode.QRCode(version=2, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("/tmp/xhs_qr.png")
    print("Saved to /tmp/xhs_qr.png")
```

### 3. 发送图片给用户

```
MEDIA:/tmp/xhs_qr.png
```

用户扫码后，在 NAS 上验证：
```bash
xhs search "test"
```

## 关键依赖

- `camoufox`：xhs cli 自带，路径 `/home/banana/.local/share/uv/tools/xhs-cli/lib/python3.11/site-packages/`
- `qrcode` + `Pillow`：需手动安装（pip install qrcode pillow）
- xhs cli 本身：`~/.local/bin/xhs`

## 完整登录流程（自动等待扫码 + 存 cookies）

camoufox 是异步库，其 `expect_response`/`wait_for_response` 必须在主线程的 asyncio 事件循环中调用，不能放在后台线程——否则会报 `no current event loop in thread`。

正确做法：用主线程顺序执行，生成 QR 后**阻塞等待**扫码完成（最多4分钟），扫码确认后立即从浏览器上下文导出 cookies 并保存。

```python
import sys, time, json
sys.path.insert(0, '/home/banana/.local/share/uv/tools/xhs-cli/lib/python3.11/site-packages')

from camoufox.sync_api import Camoufox
import qrcode
from pathlib import Path

QR_CREATE_ENDPOINT = "/api/sns/web/v1/login/qrcode/create"
QR_STATUS_ENDPOINT = "/api/sns/web/v1/login/qrcode/status"
LOGIN_URL = "https://www.xiaohongshu.com/login"
CONFIG_DIR = Path.home() / ".xhs-cli"
COOKIE_FILE = CONFIG_DIR / "cookies.json"

BROWSER_EXPORT_COOKIE_NAMES = (
    "a1", "webId", "web_session", "web_session_sec", "id_token",
    "websectiga", "sec_poison_id", "xsecappid", "gid", "abRequestId",
    "webBuild", "loadts",
)

with Camoufox(headless=True) as browser:
    page = browser.new_page()

    # 1. 获取 QR URL
    with page.expect_response(
        lambda r: QR_CREATE_ENDPOINT in r.url and r.request.method == "POST",
        timeout=20_000,
    ) as qr_resp_info:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20_000)

    qr_payload = qr_resp_info.value.json()
    qr_data = qr_payload.get("data", qr_payload)
    qr_url = str(qr_data.get("url", "")).strip()

    # 2. 生成 QR 图片并发给用户
    qr = qrcode.QRCode(version=2, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("/tmp/xhs_qr.png")
    print("QR_SAVED")  # 通知主会话发图片

    # 3. 阻塞等待扫码（最多4分钟，在 Discord 等平台发消息让用户扫码）
    try:
        with page.expect_response(
            lambda r: QR_STATUS_ENDPOINT in r.url and r.request.method == "GET",
            timeout=240_000,
        ):
            pass
        print("SCAN_DONE")
    except Exception as e:
        print(f"TIMEOUT: {e}")
        sys.exit(1)

    time.sleep(1)

    # 4. 导出 cookies
    raw_cookies = page.context.cookies()
    cookies = {}
    for entry in raw_cookies:
        name = entry.get("name")
        value = entry.get("value")
        domain = entry.get("domain", "")
        if name in BROWSER_EXPORT_COOKIE_NAMES and "xiaohongshu.com" in domain:
            cookies[name] = value

    # 5. 保存
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    COOKIE_FILE.write_text(json.dumps({"cookies": cookies}, indent=2))
    COOKIE_FILE.chmod(0o600)
    print(f"SAVED: {list(cookies.keys())}")
```

**注意**：camoufox 不支持 `headless=False`（NAS 无显示器），`headlessless=True` 不是有效参数。登录必须通过 QR 码让用户用小红书 App 扫码，无法在 NAS 本地显示。

## 备选方案：Mac Chrome cookies 提取

如果 Mac Chrome 已登录小红书，可绕过 QR 流程，直接提取 cookies：

```bash
# 在 NAS 上执行（需要 Mac 开启 Chrome Remote Debugging 或解锁 keychain）
ssh Mac主机 "python3 -c \"
import browser_cookie3
cookies = browser_cookie3.chrome(domain_name='.xiaohongshu.com')
for c in cookies:
    if c.name in ('a1', 'web_session'):
        print(f'{c.name}={c.value}')
\""
```

Mac Chrome 的小红书 cookies 比 QR 登录更可靠。

## 踩坑记录

- camoufox `expect_response` 是异步 API，**不能放在 threading.Thread 中调用**——会在子线程中报 `no current event loop in thread`
- 正确方式：主线程阻塞调用，Python GIL 保障下 camoufox 的异步等待对单线程无影响
- 直接 curl POST 小红书 QR API 会返回 404/406，需要先访问登录页建立 session（cookie 等）
- camoufox 的 `expect_response` 是最可靠的拦截方式
- qrcode 库默认用 `border=0` 会导致扫码困难，始终用 `border=2`
- `headlessless` 不是有效参数，会导致 `TypeError: got unexpected keyword argument 'headlessless'`
