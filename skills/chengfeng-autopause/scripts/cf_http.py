#!/usr/bin/env python3
"""
cf_http.py - 用保存的 Cookie 直接向千帆 API 发请求，不需要 Chrome 常开。

依赖: cf_cookie.py 已提取 cookies（~/.opencli/sessions/chengfeng.cookies.json）

覆盖的 API：
  创意层：list / status-update（pause/resume）/ budget-update
  计划层：list / status-update（pause/resume）/ budget-update
  数据层：summary（汇总）/ trend（趋势/日报）/ report（自定义报表）
  账户层：account-info / balance
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta

COOKIE_FILE = os.path.expanduser("~/.opencli/sessions/chengfeng.cookies.json")
BASE_URL = "https://chengfeng.xiaohongshu.com"
API_BASE = f"{BASE_URL}/api/wind"

# ─── 全量 columns ────────────────────────────────────────────────────────────

# 创意层 / 计划层共用的核心指标（精简版，去掉低频指标）
CORE_COLUMNS = [
    "fee", "impression", "click", "ctr", "acp", "cpm",
    "like", "comment", "collect", "follow", "share", "interaction",
    "cpi", "actionButtonClick", "actionButtonCtr",
    "videoPlayCnt", "videoPlay5sCnt", "videoPlay5sRate",
    "goodsViewNum", "goodsViewNumCost", "goodsAddCartNum", "goodsAddCartNumCost",
    "totalOrderNum7d", "totalOrderNum7dCost", "totalOrderGmv7d", "totalOrderRoi7d",
    "dealOrderNum7d", "dealOrderNum7dCost", "dealOrderGmv7d", "dealOrderRoi7d", "dealOrderCvr7d",
    "directDealOrderNum24h", "directDealOrderNum24hCost",
    "directDealOrderGmv24h", "directDealOrderGmv24hRoi",
]

# 直播专用指标
LIVE_COLUMNS = [
    "liveWatchCnt", "liveWatchCntCost", "liveFollowCnt",
    "live5sWatchCnt", "live5sWatchCntCost",
    "liveDirectDealOrderNum24h", "liveDirectDealOrderNum24hCost",
    "liveDirectDealOrderGmv24h", "liveDirectDealOrderRoi24h",
    "liveDirectPurchaseOrderNum24h", "liveDirectPurchaseOrderNum24hCost",
    "liveDirectPurchaseOrderGmv24h", "liveDirectPurchaseOrderRoi24h",
]

# 搜索专用指标
SEARCH_COLUMNS = [
    "searchFirstShowImpNum", "searchFirstShowClickNum", "searchFirstShowFee",
    "searchFirstShowImpRatio", "searchFirstShowClickRatio", "searchFirstShowFeeRatio",
    "searchCmtClick", "searchCmtClickCvr", "searchCmtAfterReadAvg", "searchCmtAfterRead",
]

# 全量（SKILL.md 里的完整 columns）
FULL_COLUMNS = CORE_COLUMNS + LIVE_COLUMNS + SEARCH_COLUMNS + [
    "screenshot", "picSave", "reservePV",
    "liveSubscribeCnt", "liveSubscribeCntCost", "liveWatchDurationAvg",
    "liveCmtCnt", "live30sWatchCnt", "live30sWatchCntCost",
    "liveDirectGoodsViewNum24h", "liveDirectGoodsViewNum24hCost",
    "liveDirectGoodsAddCartNum24h", "liveDirectGoodsAddCartNum24hCost",
    "totalOrderNum7dByCvr", "totalOrderNum7dCostByCvr", "totalOrderGmv7dByCvr", "totalOrderRoi7dByCvr",
    "dealOrderNum7dByCvr", "dealOrderNum7dCostByCvr", "dealOrderGmv7dByCvr", "dealOrderRoi7dByCvr",
    "salesDirectPurchaseOrderNum24h", "salesDirectPurchaseOrderNum24hCost",
    "salesDirectPurchaseOrderGmv24h", "salesDirectPurchaseOrderGmv24hRoi",
    "salesDirectDealOrderNum24h", "salesDirectDealOrderNum24hCost",
    "salesDirectDealOrderGmv24h", "salesDirectDealOrderGmv24hRoi",
    "newSellerGoodsViewNum", "newSellerDealOrderNum7d", "newSellerDealOrderGmv7d",
    "newSellerLiveDirectDealOrderNum24h", "newSellerLiveDirectDealOrderGmv24h",
]

# 营销目标（乘风计划全部目标）
DEFAULT_MARKETING_TARGETS = [3, 4, 15]


# ─── Cookie 工具 ─────────────────────────────────────────────────────────────

def load_cookies() -> dict:
    if not os.path.exists(COOKIE_FILE):
        print(f"[!] Cookie 文件不存在: {COOKIE_FILE}", file=sys.stderr)
        print("    请先运行: python3 cf_cli.py login", file=sys.stderr)
        sys.exit(1)
    with open(COOKIE_FILE) as f:
        return json.load(f)


def build_cookie_header(data: dict) -> str:
    return "; ".join(
        f"{c['name']}={c['value']}"
        for c in data.get("cookies", [])
        if c.get("value") and c.get("name")
    )


def get_common_headers(cookie_str: str) -> dict:
    return {
        "Cookie": cookie_str,
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://chengfeng.xiaohongshu.com/cf/ad/manage",
        "Origin": "https://chengfeng.xiaohongshu.com",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }


# ─── HTTP 基础工具 ────────────────────────────────────────────────────────────

def _post(url: str, body: dict, headers: dict) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code}: {err_body[:400]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def _get(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {e.code}: {err_body[:400]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误: {e.reason}")


def _check_resp(resp: dict, label: str = "") -> dict:
    """统一检查 API 响应 code，非 0 则抛异常。"""
    code = resp.get("code", -1)
    if code != 0:
        msg = resp.get("msg", "未知错误")
        raise RuntimeError(f"API 错误{' (' + label + ')' if label else ''}: {msg} (code={code})")
    return resp


# ─── 日期工具 ────────────────────────────────────────────────────────────────

def default_date_range(days: int = 7) -> tuple:
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
    return start, end


def date_range_list(start: str, end: str) -> list:
    """生成 start～end 之间的所有日期字符串列表（用于趋势）。"""
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    result = []
    while s <= e:
        result.append(s.strftime("%Y-%m-%d"))
        s += timedelta(days=1)
    return result


# ─── 创意层 API ──────────────────────────────────────────────────────────────

def fetch_creativity_list(headers: dict, start_date: str, end_date: str,
                          page: int = 1, page_size: int = 20,
                          columns: list = None,
                          marketing_targets: list = None,
                          status_filter: str = None,
                          plan_id: str = None) -> dict:
    """
    获取创意列表。
    status_filter: None=全部, 'ACTIVE'=有效, 'PAUSE'=暂停
    plan_id: 只看某个计划下的创意
    """
    body = {
        "page": {"pageIndex": page, "pageSize": page_size},
        "columns": columns or CORE_COLUMNS,
        "marketingTargetList": marketing_targets or DEFAULT_MARKETING_TARGETS,
        "startTime": start_date,
        "endTime": end_date,
    }
    if status_filter:
        body["statusList"] = [status_filter]
    if plan_id:
        body["creativitySetId"] = plan_id  # 计划ID过滤
    resp = _post(f"{API_BASE}/creativity/list", body, headers)
    return _check_resp(resp, "creativity/list")


def fetch_all_creativity(headers: dict, start_date: str, end_date: str,
                         columns: list = None,
                         status_filter: str = None,
                         plan_id: str = None,
                         page_size: int = 50) -> list:
    """自动翻页获取全部创意（最多 100 页保护上限）。"""
    all_rows = []
    page = 1
    while True:
        print(f"  [*] 创意 第 {page} 页...", file=sys.stderr)
        resp = fetch_creativity_list(
            headers, start_date, end_date, page, page_size,
            columns=columns, status_filter=status_filter, plan_id=plan_id
        )
        data = resp.get("data", {})
        total_page = int(data.get("totalPage", 1))
        rows = parse_creativity_rows(resp)
        all_rows.extend(rows)
        if page >= total_page or page >= 100:
            if total_page > 1:
                print(f"  [✓] 创意共 {len(all_rows)} 条（{total_page} 页）", file=sys.stderr)
            break
        page += 1
    return all_rows


def parse_creativity_rows(resp: dict) -> list:
    """解析 creativity/list 响应，返回结构化列表。"""
    rows = []
    for row in resp.get("data", {}).get("dataList", []):
        try:
            vals = json.loads(row.get("dataValueJson", "{}"))
        except Exception:
            vals = {}
        vals["_id"] = row.get("creativityId") or row.get("id", "")
        vals["_name"] = row.get("name") or row.get("title", "")
        vals["_status"] = row.get("status", "")
        vals["_planId"] = row.get("creativitySetId") or row.get("planId", "")
        vals["_planName"] = row.get("creativitySetName") or row.get("planName", "")
        vals["_noteId"] = row.get("noteId", "")
        vals["_marketingTarget"] = row.get("marketingTarget", "")
        vals["_budget"] = row.get("budget", "")
        vals["_bid"] = row.get("bid", "")
        vals["_type"] = "creativity"
        rows.append(vals)
    return rows


def update_creativity_status(headers: dict, creativity_id: str, status: str) -> dict:
    """
    更新创意状态。
    status: 'PAUSE'=暂停, 'ACTIVE'=启用/恢复
    """
    body = {"creativityId": creativity_id, "status": status}
    resp = _post(f"{API_BASE}/creativity/status/update", body, headers)
    return resp  # 不抛异常，让批量操作自己处理


def batch_update_creativity_status(headers: dict, ids: list, status: str,
                                   dry_run: bool = False) -> list:
    """批量更新创意状态。返回每条的结果列表。"""
    label = {"PAUSE": "暂停", "ACTIVE": "启用"}.get(status, status)
    results = []
    for cid in ids:
        if dry_run:
            print(f"  [DRY-RUN] {label}: {cid}")
            results.append({"id": cid, "success": True, "dry_run": True})
            continue
        try:
            resp = update_creativity_status(headers, cid, status)
            ok = resp.get("code") == 0 or resp.get("success") is True
            results.append({"id": cid, "success": ok, "msg": resp.get("msg", ""), "code": resp.get("code")})
            icon = "✓" if ok else "✗"
            print(f"  [{icon}] {label} 创意 {cid}: {resp.get('msg', '')}")
        except Exception as e:
            results.append({"id": cid, "success": False, "error": str(e)})
            print(f"  [✗] {label} 创意 {cid} 失败: {e}")
    return results


def update_creativity_budget(headers: dict, creativity_id: str, budget: float) -> dict:
    """修改单个创意日预算（元）。"""
    body = {"creativityId": creativity_id, "budget": budget}
    resp = _post(f"{API_BASE}/creativity/budget/update", body, headers)
    return resp


def update_creativity_bid(headers: dict, creativity_id: str, bid: float) -> dict:
    """修改单个创意出价（元）。"""
    body = {"creativityId": creativity_id, "bid": bid}
    resp = _post(f"{API_BASE}/creativity/bid/update", body, headers)
    return resp


# ─── 计划层 API (creativity_set) ─────────────────────────────────────────────

def fetch_plan_list(headers: dict, start_date: str, end_date: str,
                    page: int = 1, page_size: int = 20,
                    columns: list = None,
                    marketing_targets: list = None,
                    status_filter: str = None) -> dict:
    """
    获取计划（广告组）列表。
    status_filter: None=全部, 'ACTIVE'=有效, 'PAUSE'=暂停
    """
    body = {
        "page": {"pageIndex": page, "pageSize": page_size},
        "columns": columns or CORE_COLUMNS,
        "marketingTargetList": marketing_targets or DEFAULT_MARKETING_TARGETS,
        "startTime": start_date,
        "endTime": end_date,
    }
    if status_filter:
        body["statusList"] = [status_filter]
    resp = _post(f"{API_BASE}/creativity_set/list", body, headers)
    return _check_resp(resp, "creativity_set/list")


def fetch_all_plans(headers: dict, start_date: str, end_date: str,
                    columns: list = None,
                    status_filter: str = None,
                    page_size: int = 50) -> list:
    """自动翻页获取全部计划。"""
    all_rows = []
    page = 1
    while True:
        print(f"  [*] 计划 第 {page} 页...", file=sys.stderr)
        resp = fetch_plan_list(
            headers, start_date, end_date, page, page_size,
            columns=columns, status_filter=status_filter
        )
        data = resp.get("data", {})
        total_page = int(data.get("totalPage", 1))
        rows = parse_plan_rows(resp)
        all_rows.extend(rows)
        if page >= total_page or page >= 100:
            if total_page > 1:
                print(f"  [✓] 计划共 {len(all_rows)} 条（{total_page} 页）", file=sys.stderr)
            break
        page += 1
    return all_rows


def parse_plan_rows(resp: dict) -> list:
    """解析 creativity_set/list 响应。"""
    rows = []
    for row in resp.get("data", {}).get("dataList", []):
        try:
            vals = json.loads(row.get("dataValueJson", "{}"))
        except Exception:
            vals = {}
        vals["_id"] = row.get("creativitySetId") or row.get("id", "")
        vals["_name"] = row.get("name") or row.get("title", "")
        vals["_status"] = row.get("status", "")
        vals["_marketingTarget"] = row.get("marketingTarget", "")
        vals["_budget"] = row.get("budget", "")
        vals["_bid"] = row.get("bid", "")
        vals["_creativityCount"] = row.get("creativityCount", "")
        vals["_type"] = "plan"
        rows.append(vals)
    return rows


def update_plan_status(headers: dict, plan_id: str, status: str) -> dict:
    """更新计划状态。status: 'PAUSE' | 'ACTIVE'"""
    body = {"creativitySetId": plan_id, "status": status}
    resp = _post(f"{API_BASE}/creativity_set/status/update", body, headers)
    return resp


def batch_update_plan_status(headers: dict, ids: list, status: str,
                              dry_run: bool = False) -> list:
    """批量更新计划状态。"""
    label = {"PAUSE": "暂停", "ACTIVE": "启用"}.get(status, status)
    results = []
    for pid in ids:
        if dry_run:
            print(f"  [DRY-RUN] {label} 计划: {pid}")
            results.append({"id": pid, "success": True, "dry_run": True})
            continue
        try:
            resp = update_plan_status(headers, pid, status)
            ok = resp.get("code") == 0 or resp.get("success") is True
            results.append({"id": pid, "success": ok, "msg": resp.get("msg", "")})
            icon = "✓" if ok else "✗"
            print(f"  [{icon}] {label} 计划 {pid}: {resp.get('msg', '')}")
        except Exception as e:
            results.append({"id": pid, "success": False, "error": str(e)})
            print(f"  [✗] {label} 计划 {pid} 失败: {e}")
    return results


def update_plan_budget(headers: dict, plan_id: str, budget: float) -> dict:
    """修改计划日预算（元）。"""
    body = {"creativitySetId": plan_id, "budget": budget}
    resp = _post(f"{API_BASE}/creativity_set/budget/update", body, headers)
    return resp


def update_plan_bid(headers: dict, plan_id: str, bid: float) -> dict:
    """修改计划出价（元）。"""
    body = {"creativitySetId": plan_id, "bid": bid}
    resp = _post(f"{API_BASE}/creativity_set/bid/update", body, headers)
    return resp


# ─── 数据汇总 API ─────────────────────────────────────────────────────────────

def fetch_account_summary(headers: dict, start_date: str, end_date: str,
                          columns: list = None) -> dict:
    """
    获取账户级别汇总数据。
    使用 data/report 接口，granularity=ACCOUNT。
    """
    body = {
        "startTime": start_date,
        "endTime": end_date,
        "granularity": "ACCOUNT",
        "columns": columns or CORE_COLUMNS,
        "marketingTargetList": DEFAULT_MARKETING_TARGETS,
    }
    resp = _post(f"{API_BASE}/data/report", body, headers)
    return _check_resp(resp, "data/report account")


def fetch_trend(headers: dict, start_date: str, end_date: str,
                granularity: str = "DAY",
                level: str = "ACCOUNT",
                columns: list = None) -> dict:
    """
    获取趋势/日报数据。
    granularity: 'DAY' | 'HOUR'
    level: 'ACCOUNT' | 'CREATIVITY_SET' | 'CREATIVITY'
    """
    body = {
        "startTime": start_date,
        "endTime": end_date,
        "granularity": granularity,
        "level": level,
        "columns": columns or ["fee", "impression", "click", "ctr",
                               "dealOrderNum7d", "dealOrderGmv7d", "dealOrderRoi7d"],
        "marketingTargetList": DEFAULT_MARKETING_TARGETS,
    }
    resp = _post(f"{API_BASE}/data/report", body, headers)
    return _check_resp(resp, f"data/report trend {level}")


def fetch_balance(headers: dict) -> dict:
    """获取账户余额信息。"""
    resp = _get(f"{API_BASE}/account/balance", headers)
    return resp


def fetch_account_info(headers: dict) -> dict:
    """获取账户基本信息。"""
    resp = _get(f"{API_BASE}/account/info", headers)
    return resp


# ─── 解析辅助 ────────────────────────────────────────────────────────────────

def parse_rows(resp: dict, row_type: str = "creativity") -> list:
    """通用行解析入口，根据 row_type 分发。"""
    if row_type == "plan":
        return parse_plan_rows(resp)
    return parse_creativity_rows(resp)


def safe_float(val, default=0.0) -> float:
    """安全转换为 float，支持 '72.19元' 等带单位字符串。"""
    try:
        return float(str(val).replace("元", "").replace("%", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return default


# ─── 打印工具 ────────────────────────────────────────────────────────────────

def print_creativity_table(rows: list):
    if not rows:
        print("  （无创意数据）")
        return
    print(f"\n  {'ID':<16} {'名称':<22} {'状态':<6} {'消耗(元)':>10} {'成交笔':>6} {'GMV(元)':>12} {'ROI':>7} {'展现':>8} {'点击':>7}")
    print(f"  {'─'*95}")
    for r in rows:
        cid = str(r.get("_id", ""))[:16]
        name = str(r.get("_name") or "")[:22]
        status = str(r.get("_status") or "")[:6]
        fee = str(r.get("fee", "-"))
        deal = str(r.get("dealOrderNum7d", "-"))
        gmv = str(r.get("dealOrderGmv7d", "-"))
        roi = str(r.get("dealOrderRoi7d", "-"))
        imp = str(r.get("impression", "-"))
        click = str(r.get("click", "-"))
        print(f"  {cid:<16} {name:<22} {status:<6} {fee:>10} {deal:>6} {gmv:>12} {roi:>7} {imp:>8} {click:>7}")


def print_plan_table(rows: list):
    if not rows:
        print("  （无计划数据）")
        return
    print(f"\n  {'ID':<16} {'名称':<25} {'状态':<6} {'消耗(元)':>10} {'成交笔':>6} {'GMV(元)':>12} {'ROI':>7} {'创意数':>6}")
    print(f"  {'─'*90}")
    for r in rows:
        pid = str(r.get("_id", ""))[:16]
        name = str(r.get("_name") or "")[:25]
        status = str(r.get("_status") or "")[:6]
        fee = str(r.get("fee", "-"))
        deal = str(r.get("dealOrderNum7d", "-"))
        gmv = str(r.get("dealOrderGmv7d", "-"))
        roi = str(r.get("dealOrderRoi7d", "-"))
        cnt = str(r.get("_creativityCount", "-"))
        print(f"  {pid:<16} {name:<25} {status:<6} {fee:>10} {deal:>6} {gmv:>12} {roi:>7} {cnt:>6}")


def print_summary_table(rows: list, title: str = "汇总"):
    """打印汇总/趋势数据表格。"""
    if not rows:
        print("  （无数据）")
        return
    # 自动识别有值的列
    key_cols = ["date", "fee", "impression", "click", "ctr",
                "dealOrderNum7d", "dealOrderGmv7d", "dealOrderRoi7d"]
    print(f"\n  {title}")
    header = f"  {'日期/维度':<14} {'消耗(元)':>12} {'展现':>10} {'点击':>8} {'点击率':>8} {'成交笔':>7} {'GMV':>12} {'ROI':>7}"
    print(header)
    print(f"  {'─'*80}")
    for r in rows:
        date = str(r.get("date") or r.get("_id") or "-")[:14]
        fee = str(r.get("fee", "-"))
        imp = str(r.get("impression", "-"))
        clk = str(r.get("click", "-"))
        ctr = str(r.get("ctr", "-"))
        deal = str(r.get("dealOrderNum7d", "-"))
        gmv = str(r.get("dealOrderGmv7d", "-"))
        roi = str(r.get("dealOrderRoi7d", "-"))
        print(f"  {date:<14} {fee:>12} {imp:>10} {clk:>8} {ctr:>8} {deal:>7} {gmv:>12} {roi:>7}")
