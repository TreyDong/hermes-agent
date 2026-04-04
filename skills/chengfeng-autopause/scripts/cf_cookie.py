#!/usr/bin/env python3
"""
cf_cookie.py - 从本机真实 Chrome 数据库直接读取千帆 cookies（无需 CDP / 无需 Chrome 开调试端口）

原理：
  macOS Chrome 把 cookies 加密存在 SQLite 文件里
  加密 key 存在 macOS Keychain（Chrome Safe Storage）
  解密方式：AES-128-CBC，key = PBKDF2(keychain_password, salt='saltysalt', iter=1003)

用法:
    python3 cf_cookie.py              # 提取并保存 cookies
    python3 cf_cookie.py --show       # 打印已保存的 cookies
    python3 cf_cookie.py --check      # 验证 cookies 是否有效
    python3 cf_cookie.py --raw        # 打印从 Chrome 读取的原始 cookie 名称（不解密值）

保存路径: ~/.opencli/sessions/chengfeng.cookies.json
"""

import json
import os
import shutil
import sqlite3
import struct
import subprocess
import sys
import argparse
import urllib.request
from datetime import datetime

COOKIE_FILE = os.path.expanduser("~/.opencli/sessions/chengfeng.cookies.json")
CHROME_COOKIE_DB = os.path.expanduser(
    "~/Library/Application Support/Google/Chrome/Default/Cookies"
)
TARGET_DOMAIN = "chengfeng.xiaohongshu.com"
RELATED_DOMAINS = ["xiaohongshu.com"]  # host_key LIKE 匹配


# ─── Keychain + AES 解密 ──────────────────────────────────────────────────────

def _get_keychain_password() -> bytes:
    """从 macOS Keychain 读取 Chrome Safe Storage 密码。"""
    result = subprocess.run(
        ["security", "find-generic-password",
         "-a", "Chrome", "-s", "Chrome Safe Storage", "-w"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "无法从 Keychain 读取 Chrome Safe Storage 密码，"
            "请在系统提示时点击「允许」\n" + result.stderr.strip()
        )
    return result.stdout.strip().encode("utf-8")


def _derive_key(password: bytes) -> bytes:
    """PBKDF2-SHA1 派生 AES key（macOS Chrome 固定参数）。"""
    import hashlib
    key = hashlib.pbkdf2_hmac(
        "sha1",
        password,
        b"saltysalt",  # macOS Chrome 固定 salt
        1003,           # macOS Chrome 固定迭代次数
        dklen=16,       # AES-128
    )
    return key


def _decrypt_value(encrypted: bytes, key: bytes) -> str:
    """
    解密 Chrome cookie 值。
    格式：b'v10' + IV(16字节) + 密文 （macOS Chrome v10 格式）
    """
    if not encrypted:
        return ""

    # 明文 cookie（旧版或未加密）
    if not encrypted.startswith(b"v10"):
        try:
            return encrypted.decode("utf-8")
        except Exception:
            return ""

    try:
        from Crypto.Cipher import AES
    except ImportError:
        # 没有 pycryptodome，尝试用 cryptography 库
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            iv = b" " * 16
            ciphertext = encrypted[3:]  # 去掉 'v10'
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(ciphertext) + decryptor.finalize()
            # 去掉 PKCS7 padding
            pad_len = decrypted[-1]
            return decrypted[:-pad_len].decode("utf-8", errors="replace")
        except ImportError:
            raise RuntimeError(
                "需要安装解密库，请运行：\n"
                "  pip3 install pycryptodome\n"
                "或：\n"
                "  pip3 install cryptography"
            )

    iv = b" " * 16  # macOS Chrome CBC IV 是 16 个空格
    ciphertext = encrypted[3:]  # 去掉 'v10' 前缀
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)
    decrypted = cipher.decrypt(ciphertext)
    # 去掉 PKCS7 padding
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode("utf-8", errors="replace")


# ─── 读取 Chrome cookies ──────────────────────────────────────────────────────

def extract_cookies() -> dict:
    """
    从本机 Chrome SQLite 数据库读取并解密千帆相关 cookies。
    Chrome 运行时会锁定数据库，所以先复制一份再读。
    """
    if not os.path.exists(CHROME_COOKIE_DB):
        raise RuntimeError(f"Chrome cookie 数据库不存在: {CHROME_COOKIE_DB}")

    # 复制（Chrome 运行中文件被锁，复制可以绕过）
    tmp_db = "/tmp/cf_chrome_cookies_extract.db"
    shutil.copy2(CHROME_COOKIE_DB, tmp_db)

    print("[*] 从 Keychain 读取解密 key...", file=sys.stderr)
    password = _get_keychain_password()
    key = _derive_key(password)

    print("[*] 读取 Chrome cookie 数据库...", file=sys.stderr)
    conn = sqlite3.connect(tmp_db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 查询所有 xiaohongshu.com 相关 cookies
    placeholders = " OR ".join(["host_key LIKE ?"] * len(RELATED_DOMAINS))
    params = [f"%{d}" for d in RELATED_DOMAINS]
    cur.execute(
        f"SELECT name, host_key, path, encrypted_value, expires_utc, "
        f"is_httponly, is_secure, samesite FROM cookies "
        f"WHERE {placeholders} ORDER BY host_key, name",
        params,
    )
    rows = cur.fetchall()
    conn.close()
    os.unlink(tmp_db)

    cookies = []
    failed = 0
    for row in rows:
        try:
            value = _decrypt_value(bytes(row["encrypted_value"]), key)
        except Exception as e:
            value = ""
            failed += 1

        # Chrome 时间戳是微秒，从 1601-01-01 起算
        expires_utc = row["expires_utc"]
        expires_unix = (expires_utc / 1_000_000 - 11644473600) if expires_utc else 0

        cookies.append({
            "name": row["name"],
            "value": value,
            "domain": row["host_key"],
            "path": row["path"],
            "expires": expires_unix,
            "httpOnly": bool(row["is_httponly"]),
            "secure": bool(row["is_secure"]),
        })

    if failed:
        print(f"  [!] {failed} 条 cookie 解密失败（可能需要安装 pycryptodome）", file=sys.stderr)

    print(f"  [✓] 读取到 {len(cookies)} 条 xiaohongshu cookie", file=sys.stderr)
    return {
        "extracted_at": datetime.now().isoformat(),
        "domain": TARGET_DOMAIN,
        "cookies": cookies,
    }


# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def ensure_dir():
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)


def save_cookies(data: dict):
    ensure_dir()
    with open(COOKIE_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✓] Cookies 已保存到: {COOKIE_FILE}", file=sys.stderr)
    print(f"    共 {len(data['cookies'])} 条 cookie", file=sys.stderr)


def load_cookies() -> dict:
    if not os.path.exists(COOKIE_FILE):
        print(f"[!] Cookie 文件不存在: {COOKIE_FILE}", file=sys.stderr)
        print("    请先运行: python3 cf_cookie.py", file=sys.stderr)
        sys.exit(1)
    with open(COOKIE_FILE) as f:
        return json.load(f)


def cookies_to_header(data: dict) -> str:
    """把 cookies 转成 HTTP Cookie header 字符串，跳过空值。"""
    return "; ".join(
        f"{c['name']}={c['value']}"
        for c in data.get("cookies", [])
        if c.get("value") and c.get("name")
    )


# 兼容别名
build_cookie_header = cookies_to_header


def check_cookies(data: dict) -> bool:
    """发一次 API 请求验证 cookies 是否有效（401 = 过期）。"""
    cookie_str = cookies_to_header(data)
    if not cookie_str:
        print("[!] cookies 为空", file=sys.stderr)
        return False

    import urllib.request, urllib.error
    req = urllib.request.Request(
        "https://chengfeng.xiaohongshu.com/api/wind/creativity/list",
        data=b'{"page":{"pageIndex":1,"pageSize":1},"columns":["fee"],'
             b'"marketingTargetList":[3],"startTime":"2026-04-01","endTime":"2026-04-04"}',
        headers={
            "Cookie": cookie_str,
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://chengfeng.xiaohongshu.com/cf/ad/manage",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("code") == 0 or body.get("success"):
                print(f"[✓] Cookies 有效（API 返回正常）", file=sys.stderr)
                return True
            if body.get("code") in (-100, 401):
                print(f"[!] Cookies 已过期（{body.get('msg')}），请重新运行: python3 cf_cookie.py", file=sys.stderr)
                return False
            print(f"[?] API 返回: code={body.get('code')} msg={body.get('msg')}", file=sys.stderr)
            return True  # 有返回就算有效
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[!] Cookies 已过期（HTTP 401）", file=sys.stderr)
            return False
        print(f"[!] HTTP {e.code}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[!] 验证失败: {e}", file=sys.stderr)
        return False


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="千帆 Cookie 提取工具（直读 Chrome 数据库）")
    parser.add_argument("--show", action="store_true", help="打印已保存的 cookies")
    parser.add_argument("--check", action="store_true", help="验证 cookies 是否有效")
    parser.add_argument("--raw", action="store_true", help="打印从 Chrome 读取的原始 cookie 名称")
    args = parser.parse_args()

    if args.show:
        data = load_cookies()
        print(f"提取时间: {data.get('extracted_at', '未知')}")
        print(f"共 {len(data.get('cookies', []))} 条 cookie:\n")
        for c in data.get("cookies", []):
            exp = c.get("expires", 0)
            exp_str = datetime.fromtimestamp(exp).strftime("%Y-%m-%d") if exp and exp > 0 else "会话"
            httponly = " [HttpOnly]" if c.get("httpOnly") else ""
            print(f"  {c['name']:<45} expires={exp_str}{httponly}")
        return

    if args.check:
        data = load_cookies()
        ok = check_cookies(data)
        sys.exit(0 if ok else 1)

    if args.raw:
        tmp_db = "/tmp/cf_chrome_cookies_raw.db"
        shutil.copy2(CHROME_COOKIE_DB, tmp_db)
        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        cur.execute(
            "SELECT name, host_key, is_httponly FROM cookies "
            "WHERE host_key LIKE '%xiaohongshu%' ORDER BY host_key, name"
        )
        print(f"{'Cookie名':<50} {'Domain':<40} HttpOnly")
        print("─" * 100)
        for name, host, httponly in cur.fetchall():
            print(f"  {name:<48} {host:<40} {'是' if httponly else ''}")
        conn.close()
        os.unlink(tmp_db)
        return

    # 默认：提取并保存
    try:
        data = extract_cookies()
    except RuntimeError as e:
        print(f"[!] {e}", file=sys.stderr)
        sys.exit(1)

    if not data.get("cookies"):
        print("[!] 未读取到任何 cookie", file=sys.stderr)
        sys.exit(1)

    save_cookies(data)
    print(f"\n[✓] 完成。运行 python3 cf_cookie.py --check 验证是否能调用 API。", file=sys.stderr)


if __name__ == "__main__":
    main()
