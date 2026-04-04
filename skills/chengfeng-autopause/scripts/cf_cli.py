#!/usr/bin/env python3
"""
cf_cli.py - 千帆创意自动停投 主 CLI

全部命令:
  ── 登录 ──
  login           从 Chrome CDP Session 提取并保存 cookies（首次 / 过期时）
  check           验证保存的 cookies 是否有效

  ── 创意（默认层） ──
  list            列出创意数据（支持翻页、日期范围、状态过滤）
  filter          按规则筛选待停创意
  pause           暂停指定创意（需确认）
  resume          启用/恢复指定创意（需确认）
  run             一键完整停投流程：list → filter → 确认 → pause
  budget          修改创意日预算
  bid             修改创意出价

  ── 计划 ──
  plan-list       列出计划数据
  plan-filter     按规则筛选待停计划
  plan-pause      暂停指定计划（需确认）
  plan-resume     启用/恢复指定计划（需确认）
  plan-run        一键计划停投流程
  plan-budget     修改计划日预算
  plan-bid        修改计划出价

  ── 数据分析 ──
  summary         账户/创意/计划汇总数据（近7天）
  trend           日趋势数据（逐日明细）
  top             按指定指标排行（如 top --by fee --n 10）

  ── 导出 ──
  export          导出数据为 CSV 文件

用法示例:
  # 首次登录
  python3 cf_cli.py login
  python3 cf_cli.py check

  # 创意操作
  python3 cf_cli.py list
  python3 cf_cli.py list --all --status active
  python3 cf_cli.py list --start 2026-04-01 --end 2026-04-04
  python3 cf_cli.py filter --rule "消耗超过10元且成交为0"
  python3 cf_cli.py filter --rule default --all
  python3 cf_cli.py pause --ids 3996550667,3996550668
  python3 cf_cli.py resume --ids 3996550667
  python3 cf_cli.py run --rule "消耗超过10元且成交为0" --all
  python3 cf_cli.py budget --id 3996550667 --value 100
  python3 cf_cli.py bid --id 3996550667 --value 3.5

  # 计划操作
  python3 cf_cli.py plan-list
  python3 cf_cli.py plan-list --all --status active
  python3 cf_cli.py plan-filter --rule "消耗超过100元且成交为0"
  python3 cf_cli.py plan-pause --ids 123456
  python3 cf_cli.py plan-resume --ids 123456
  python3 cf_cli.py plan-run --rule "消耗超过100元且ROI低于0.3"
  python3 cf_cli.py plan-budget --id 123456 --value 500

  # 数据分析
  python3 cf_cli.py summary
  python3 cf_cli.py summary --start 2026-04-01 --end 2026-04-04
  python3 cf_cli.py trend
  python3 cf_cli.py trend --days 14
  python3 cf_cli.py top --by fee --n 10
  python3 cf_cli.py top --by dealOrderNum7d --n 10 --level plan

  # 导出
  python3 cf_cli.py export --type creativity --output cf_data.csv
  python3 cf_cli.py export --type plan --output cf_plans.csv --all
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import cf_cookie
import cf_http
import cf_filter
import cf_export


# ─── 辅助 ────────────────────────────────────────────────────────────────────

def default_dates(days: int = 7) -> tuple:
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
    return start, end


def load_headers():
    data = cf_cookie.load_cookies()
    cookie_str = cf_cookie.build_cookie_header(data)
    if not cookie_str:
        print("[!] Cookie 为空，请先运行: python3 cf_cli.py login", file=sys.stderr)
        sys.exit(1)
    extracted_at = data.get("extracted_at", "")
    print(f"[*] 使用 cookies（提取于 {extracted_at}）", file=sys.stderr)
    return cf_http.get_common_headers(cookie_str)


def resolve_rule(rule_str: str):
    """解析规则名或自然语言规则，返回 RuleSet。"""
    if rule_str in cf_filter.PRESET_RULES:
        ruleset = cf_filter.PRESET_RULES[rule_str]
        print(f"[*] 预设规则: {ruleset.description}", file=sys.stderr)
    else:
        ruleset = cf_filter.parse_natural_rule(rule_str)
        if not ruleset:
            print(f"[!] 规则解析失败: {rule_str}", file=sys.stderr)
            print("    预设规则: " + " / ".join(cf_filter.PRESET_RULES.keys()), file=sys.stderr)
            sys.exit(1)
        print(f"[*] 解析规则: {ruleset}", file=sys.stderr)
    return ruleset


def confirm_action(items: list, action: str, item_type: str, yes: bool = False) -> bool:
    if not items:
        print(f"（无需{action}）")
        return False
    if yes:
        return True
    ids = [r.get("_id", r) if isinstance(r, dict) else r for r in items]
    print(f"\n将要{action}以下 {len(ids)} 条{item_type}：")
    for x in ids:
        name = ""
        if isinstance(items[0], dict):
            name = f"  {items[ids.index(x)].get('_name', '')}"
        print(f"  - {x}{name}")
    answer = input(f"\n确认{action}？[y/N] ").strip().lower()
    return answer in ("y", "yes", "确认")


def fetch_rows(headers, start, end, all_pages, page, page_size, status_filter,
               row_type="creativity", plan_id=None, columns=None):
    """统一拉数据入口（创意 or 计划）。"""
    if row_type == "plan":
        if all_pages:
            return cf_http.fetch_all_plans(headers, start, end,
                                           status_filter=status_filter,
                                           page_size=page_size)
        resp = cf_http.fetch_plan_list(headers, start, end, page, page_size,
                                       status_filter=status_filter)
        rows = cf_http.parse_plan_rows(resp)
        total_page = resp.get("data", {}).get("totalPage", "?")
        print(f"[*] 第 {page}/{total_page} 页，共 {len(rows)} 条计划", file=sys.stderr)
        return rows
    else:
        if all_pages:
            return cf_http.fetch_all_creativity(headers, start, end,
                                                status_filter=status_filter,
                                                plan_id=plan_id,
                                                page_size=page_size,
                                                columns=columns)
        resp = cf_http.fetch_creativity_list(headers, start, end, page, page_size,
                                             status_filter=status_filter,
                                             plan_id=plan_id,
                                             columns=columns)
        rows = cf_http.parse_creativity_rows(resp)
        total_page = resp.get("data", {}).get("totalPage", "?")
        print(f"[*] 第 {page}/{total_page} 页，共 {len(rows)} 条创意", file=sys.stderr)
        return rows


# ─── 登录 ─────────────────────────────────────────────────────────────────────

def cmd_login(args):
    print("=" * 60)
    print("  千帆 Cookie 登录")
    print("=" * 60)
    print("\n前提：Chrome 已开启远程调试、agent-browser session chengfeng 已连接、千帆已登录")
    print()
    data = cf_cookie.extract_cookies()
    if not data.get("cookies"):
        print("[!] 提取失败，请检查 agent-browser session 状态")
        sys.exit(1)
    cf_cookie.save_cookies(data)
    print(f"\n[✓] 完成，共 {len(data['cookies'])} 条 cookie。")
    print("    验证: python3 cf_cli.py check")


def cmd_check(args):
    data = cf_cookie.load_cookies()
    if not data:
        print("[!] 未提取 cookies，请先运行: python3 cf_cli.py login")
        sys.exit(1)
    ok = cf_cookie.check_cookies(data)
    sys.exit(0 if ok else 1)


# ─── 创意命令 ────────────────────────────────────────────────────────────────

def cmd_list(args):
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end
    status_map = {"active": "ACTIVE", "pause": "PAUSE", "paused": "PAUSE"}
    status_filter = status_map.get((args.status or "").lower())

    rows = fetch_rows(headers, start, end, args.all,
                      getattr(args, "page", 1), getattr(args, "page_size", 20),
                      status_filter, row_type="creativity",
                      plan_id=getattr(args, "plan_id", None))

    # 排序
    if getattr(args, "sort", None):
        rows = cf_filter.sort_rows(rows, args.sort, ascending=getattr(args, "asc", False))

    print(f"\n创意列表  {start} ~ {end}  共 {len(rows)} 条")
    cf_http.print_creativity_table(rows)

    if getattr(args, "json", False):
        print(json.dumps({"rows": rows, "count": len(rows)}, indent=2, ensure_ascii=False))
    return rows


def cmd_filter(args):
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end

    print(f"[*] 拉取创意数据  {start} ~ {end}...", file=sys.stderr)
    rows = fetch_rows(headers, start, end, getattr(args, "all", False),
                      1, 50, None, row_type="creativity")

    ruleset = resolve_rule(args.rule)
    active = cf_filter.apply_status_filter(rows)
    targets = cf_filter.apply_rules(active, ruleset)

    if getattr(args, "sort", None):
        targets = cf_filter.sort_rows(targets, args.sort)
    if getattr(args, "top", None):
        targets = targets[:args.top]

    print()
    print(cf_filter.format_pause_list(targets, ruleset.description))

    if getattr(args, "json", False):
        print(json.dumps({"targets": targets, "count": len(targets)}, indent=2, ensure_ascii=False))
    return targets


def cmd_pause(args):
    headers = load_headers()
    ids = _parse_ids(args)
    rows = [{"_id": i, "_name": "", "_type": "creativity"} for i in ids]
    if not confirm_action(rows, "暂停", "创意", args.yes):
        return
    results = cf_http.batch_update_creativity_status(headers, ids, "PAUSE")
    _print_batch_result(results, "暂停", "创意")


def cmd_resume(args):
    headers = load_headers()
    ids = _parse_ids(args)
    rows = [{"_id": i, "_name": "", "_type": "creativity"} for i in ids]
    if not confirm_action(rows, "启用", "创意", args.yes):
        return
    results = cf_http.batch_update_creativity_status(headers, ids, "ACTIVE")
    _print_batch_result(results, "启用", "创意")


def cmd_run(args):
    """一键完整停投流程（创意层）。"""
    print("=" * 62)
    print("  千帆创意自动停投")
    print("=" * 62)
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end

    print(f"\n[Step 1] 拉取创意数据  {start} ~ {end}...")
    rows = fetch_rows(headers, start, end, getattr(args, "all", False),
                      1, 50, None, row_type="creativity")
    print(f"  共 {len(rows)} 条创意")

    print(f"\n[Step 2] 应用规则: {args.rule}")
    ruleset = resolve_rule(args.rule)
    active = cf_filter.apply_status_filter(rows)
    targets = cf_filter.apply_rules(active, ruleset)

    print()
    print(cf_filter.format_pause_list(targets, ruleset.description))

    if not targets:
        print("\n无需执行暂停。")
        return

    print("\n" + "─" * 62)
    if not confirm_action(targets, "暂停", "创意", args.yes):
        print("已取消。")
        return

    print(f"\n[Step 3] 执行暂停 {len(targets)} 条...")
    ids = [r["_id"] for r in targets if r.get("_id")]
    results = cf_http.batch_update_creativity_status(headers, ids, "PAUSE")
    _print_batch_result(results, "暂停", "创意")


def cmd_budget(args):
    headers = load_headers()
    cid = args.id
    val = args.value
    print(f"[*] 修改创意 {cid} 日预算 → {val} 元")
    confirm = input("确认？[y/N] ").strip().lower()
    if confirm not in ("y", "yes", "确认"):
        print("已取消")
        return
    resp = cf_http.update_creativity_budget(headers, cid, val)
    ok = resp.get("code") == 0
    print(f"[{'✓' if ok else '✗'}] {resp.get('msg', '')}")


def cmd_bid(args):
    headers = load_headers()
    cid = args.id
    val = args.value
    print(f"[*] 修改创意 {cid} 出价 → {val} 元")
    confirm = input("确认？[y/N] ").strip().lower()
    if confirm not in ("y", "yes", "确认"):
        print("已取消")
        return
    resp = cf_http.update_creativity_bid(headers, cid, val)
    ok = resp.get("code") == 0
    print(f"[{'✓' if ok else '✗'}] {resp.get('msg', '')}")


# ─── 计划命令 ────────────────────────────────────────────────────────────────

def cmd_plan_list(args):
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end
    status_map = {"active": "ACTIVE", "pause": "PAUSE", "paused": "PAUSE"}
    status_filter = status_map.get((args.status or "").lower())

    rows = fetch_rows(headers, start, end, args.all,
                      getattr(args, "page", 1), getattr(args, "page_size", 20),
                      status_filter, row_type="plan")

    if getattr(args, "sort", None):
        rows = cf_filter.sort_rows(rows, args.sort, ascending=getattr(args, "asc", False))

    print(f"\n计划列表  {start} ~ {end}  共 {len(rows)} 条")
    cf_http.print_plan_table(rows)

    if getattr(args, "json", False):
        print(json.dumps({"rows": rows, "count": len(rows)}, indent=2, ensure_ascii=False))
    return rows


def cmd_plan_filter(args):
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end

    print(f"[*] 拉取计划数据  {start} ~ {end}...", file=sys.stderr)
    rows = fetch_rows(headers, start, end, getattr(args, "all", False),
                      1, 50, None, row_type="plan")

    ruleset = resolve_rule(args.rule)
    active = cf_filter.apply_status_filter(rows)
    targets = cf_filter.apply_rules(active, ruleset)

    if getattr(args, "sort", None):
        targets = cf_filter.sort_rows(targets, args.sort)
    if getattr(args, "top", None):
        targets = targets[:args.top]

    print()
    print(cf_filter.format_pause_list(targets, ruleset.description, action="暂停"))

    if getattr(args, "json", False):
        print(json.dumps({"targets": targets, "count": len(targets)}, indent=2, ensure_ascii=False))
    return targets


def cmd_plan_pause(args):
    headers = load_headers()
    ids = _parse_ids(args)
    rows = [{"_id": i, "_name": "", "_type": "plan"} for i in ids]
    if not confirm_action(rows, "暂停", "计划", args.yes):
        return
    results = cf_http.batch_update_plan_status(headers, ids, "PAUSE")
    _print_batch_result(results, "暂停", "计划")


def cmd_plan_resume(args):
    headers = load_headers()
    ids = _parse_ids(args)
    rows = [{"_id": i, "_name": "", "_type": "plan"} for i in ids]
    if not confirm_action(rows, "启用", "计划", args.yes):
        return
    results = cf_http.batch_update_plan_status(headers, ids, "ACTIVE")
    _print_batch_result(results, "启用", "计划")


def cmd_plan_run(args):
    """一键计划停投流程。"""
    print("=" * 62)
    print("  千帆计划自动停投")
    print("=" * 62)
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end

    print(f"\n[Step 1] 拉取计划数据  {start} ~ {end}...")
    rows = fetch_rows(headers, start, end, getattr(args, "all", False),
                      1, 50, None, row_type="plan")
    print(f"  共 {len(rows)} 条计划")

    print(f"\n[Step 2] 应用规则: {args.rule}")
    ruleset = resolve_rule(args.rule)
    active = cf_filter.apply_status_filter(rows)
    targets = cf_filter.apply_rules(active, ruleset)

    print()
    print(cf_filter.format_pause_list(targets, ruleset.description))

    if not targets:
        print("\n无需执行暂停。")
        return

    print("\n" + "─" * 62)
    if not confirm_action(targets, "暂停", "计划", args.yes):
        print("已取消。")
        return

    print(f"\n[Step 3] 执行暂停 {len(targets)} 条计划...")
    ids = [r["_id"] for r in targets if r.get("_id")]
    results = cf_http.batch_update_plan_status(headers, ids, "PAUSE")
    _print_batch_result(results, "暂停", "计划")


def cmd_plan_budget(args):
    headers = load_headers()
    pid = args.id
    val = args.value
    print(f"[*] 修改计划 {pid} 日预算 → {val} 元")
    confirm = input("确认？[y/N] ").strip().lower()
    if confirm not in ("y", "yes", "确认"):
        print("已取消")
        return
    resp = cf_http.update_plan_budget(headers, pid, val)
    ok = resp.get("code") == 0
    print(f"[{'✓' if ok else '✗'}] {resp.get('msg', '')}")


def cmd_plan_bid(args):
    headers = load_headers()
    pid = args.id
    val = args.value
    print(f"[*] 修改计划 {pid} 出价 → {val} 元")
    confirm = input("确认？[y/N] ").strip().lower()
    if confirm not in ("y", "yes", "确认"):
        print("已取消")
        return
    resp = cf_http.update_plan_bid(headers, pid, val)
    ok = resp.get("code") == 0
    print(f"[{'✓' if ok else '✗'}] {resp.get('msg', '')}")


# ─── 数据分析命令 ─────────────────────────────────────────────────────────────

def cmd_summary(args):
    """账户汇总数据。"""
    headers = load_headers()
    start, end = default_dates(7)
    start = args.start or start
    end = args.end or end

    print(f"\n账户汇总数据  {start} ~ {end}")
    print("─" * 60)

    # 账户级
    try:
        resp = cf_http.fetch_account_summary(headers, start, end)
        data = resp.get("data", {})
        total_raw = data.get("totalData", "{}")
        try:
            total = json.loads(total_raw) if isinstance(total_raw, str) else total_raw
        except Exception:
            total = {}
        print(f"  {'消耗(元)':<16}: {total.get('fee', '-')}")
        print(f"  {'展现量':<16}: {total.get('impression', '-')}")
        print(f"  {'点击量':<16}: {total.get('click', '-')}")
        print(f"  {'点击率':<16}: {total.get('ctr', '-')}")
        print(f"  {'7天付款成交':<14}: {total.get('dealOrderNum7d', '-')}")
        print(f"  {'7天付款GMV':<14}: {total.get('dealOrderGmv7d', '-')}")
        print(f"  {'7天付款ROI':<14}: {total.get('dealOrderRoi7d', '-')}")
    except Exception as e:
        print(f"  [!] 汇总数据获取失败: {e}")

    # 创意层汇总
    print("\n创意层（前20条有消耗）：")
    try:
        resp2 = cf_http.fetch_creativity_list(headers, start, end, page_size=20)
        rows = cf_http.parse_creativity_rows(resp2)
        rows = [r for r in rows if cf_http.safe_float(r.get("fee")) > 0]
        rows = cf_filter.sort_rows(rows, "fee", ascending=False)
        cf_http.print_creativity_table(rows[:20])
    except Exception as e:
        print(f"  [!] 创意数据获取失败: {e}")

    # 计划层汇总
    print("\n计划层（全部）：")
    try:
        resp3 = cf_http.fetch_plan_list(headers, start, end, page_size=50)
        plan_rows = cf_http.parse_plan_rows(resp3)
        plan_rows = cf_filter.sort_rows(plan_rows, "fee", ascending=False)
        cf_http.print_plan_table(plan_rows)
    except Exception as e:
        print(f"  [!] 计划数据获取失败: {e}")


def cmd_trend(args):
    """逐日趋势数据。"""
    headers = load_headers()
    days = getattr(args, "days", 7)
    start, end = default_dates(days)
    start = args.start or start
    end = args.end or end

    level_map = {"account": "ACCOUNT", "plan": "CREATIVITY_SET", "creativity": "CREATIVITY"}
    level = level_map.get((getattr(args, "level", "account") or "account").lower(), "ACCOUNT")

    print(f"\n日趋势数据  {start} ~ {end}  维度: {level}")
    try:
        resp = cf_http.fetch_trend(headers, start, end, granularity="DAY", level=level)
        data = resp.get("data", {})
        # 趋势数据结构：dataList 每项含 date + 指标
        rows_raw = data.get("dataList", [])
        rows = []
        for row in rows_raw:
            try:
                vals = json.loads(row.get("dataValueJson", "{}"))
            except Exception:
                vals = {}
            vals["date"] = row.get("date") or row.get("time") or row.get("id", "")
            vals["_id"] = vals["date"]
            vals["_name"] = row.get("name", "")
            rows.append(vals)

        if not rows:
            # 有些接口直接返回 totalData 的日期分解
            total_raw = data.get("totalData")
            if total_raw:
                try:
                    total = json.loads(total_raw) if isinstance(total_raw, str) else total_raw
                    print(json.dumps(total, indent=2, ensure_ascii=False))
                except Exception:
                    print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print("  （趋势数据格式未知，原始输出）")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            return

        cf_http.print_summary_table(rows, title=f"日趋势（{level}）")
    except Exception as e:
        print(f"[!] 趋势数据获取失败: {e}")
        print("    千帆趋势接口可能需要额外权限或参数，建议用 summary 替代")


def cmd_top(args):
    """按指标排行 top-N。"""
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end
    by = args.by or "fee"
    n = args.n or 10
    ascending = getattr(args, "asc", False)

    level = getattr(args, "level", "creativity")
    row_type = "plan" if level == "plan" else "creativity"

    print(f"\nTop {n}  排序字段: {by}  {'升序' if ascending else '降序'}  {start} ~ {end}")
    rows = fetch_rows(headers, start, end, True, 1, 50, None, row_type=row_type)
    sorted_rows = cf_filter.sort_rows(rows, by, ascending=ascending)[:n]

    if row_type == "plan":
        cf_http.print_plan_table(sorted_rows)
    else:
        cf_http.print_creativity_table(sorted_rows)

    if getattr(args, "json", False):
        print(json.dumps({"rows": sorted_rows}, indent=2, ensure_ascii=False))


# ─── 导出命令 ─────────────────────────────────────────────────────────────────

def cmd_export(args):
    headers = load_headers()
    start, end = default_dates()
    start = args.start or start
    end = args.end or end
    row_type = getattr(args, "type", "creativity")
    output = getattr(args, "output", None) or f"cf_{row_type}_{end}.csv"

    print(f"[*] 导出 {row_type} 数据  {start} ~ {end}  → {output}")
    rows = fetch_rows(headers, start, end, getattr(args, "all", True),
                      1, 50, None, row_type=row_type)
    if not rows:
        print("（无数据）")
        return

    fmt = getattr(args, "format", "csv")
    if fmt == "json":
        cf_export.export_json(rows, output)
    else:
        cf_export.export_csv(rows, output, row_type=row_type)

    print(f"[✓] 已导出 {len(rows)} 条到 {output}")


# ─── 工具函数 ────────────────────────────────────────────────────────────────

def _parse_ids(args) -> list:
    ids = []
    if getattr(args, "id", None):
        ids = [args.id.strip()]
    elif getattr(args, "ids", None):
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    if not ids:
        print("[!] 请用 --id 或 --ids 指定 ID", file=sys.stderr)
        sys.exit(1)
    return ids


def _print_batch_result(results: list, action: str, item_type: str):
    success = sum(1 for r in results if r.get("success"))
    print(f"\n[{'✓' if success == len(results) else '!'}] {action}{item_type}完成：{success}/{len(results)} 条成功")
    for r in results:
        if not r.get("success"):
            print(f"  [✗] {r.get('id')}: {r.get('error') or r.get('msg', '')}")


# ─── 参数解析 ────────────────────────────────────────────────────────────────

def add_date_args(p):
    p.add_argument("--start", help="开始日期 YYYY-MM-DD")
    p.add_argument("--end", help="结束日期 YYYY-MM-DD")


def add_page_args(p):
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20, dest="page_size")
    p.add_argument("--all", action="store_true", help="自动翻页获取全部")


def add_status_args(p):
    p.add_argument("--status", choices=["active", "pause", "all"], default="all",
                   help="状态过滤 active/pause/all")


def add_sort_args(p):
    p.add_argument("--sort", help="排序字段，如 fee / dealOrderNum7d / dealOrderRoi7d")
    p.add_argument("--asc", action="store_true", help="升序（默认降序）")
    p.add_argument("--top", type=int, help="只显示前 N 条")


def add_id_args(p):
    p.add_argument("--id", help="单个 ID")
    p.add_argument("--ids", help="多个 ID，逗号分隔")
    p.add_argument("-y", "--yes", action="store_true", help="跳过确认")


def add_rule_args(p):
    p.add_argument("--rule", required=True,
                   help="规则名或自然语言，如 '消耗超过10元且成交为0' / default / low_roi")
    add_date_args(p)
    p.add_argument("--all", action="store_true")
    add_sort_args(p)


def main():
    parser = argparse.ArgumentParser(
        prog="cf_cli",
        description="千帆广告自动化 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
预设规则:
  default              消耗>10元 且 成交=0
  high_spend_no_deal   消耗>50元 且 成交=0
  low_roi              消耗>30元 且 ROI<0.5
  no_conversion        消耗>20元 且 展现>500 且 成交=0
  low_ctr              展现>1000 且 点击率<1%
  high_cpi             消耗>50元 且 CPI>30元
  active_only          有消耗的创意
  zero_impression      零展现（可能被限流）

自然语言规则示例:
  "消耗超过10元且成交为0"
  "消耗超过50元且ROI低于0.5"
  "消耗超过20元且展现超过500且成交为0"
  "7天GMV为0且消耗大于30"
        """,
    )
    parser.add_argument("--json", action="store_true", help="额外输出 JSON")
    sub = parser.add_subparsers(dest="cmd", title="命令")

    # ── 登录 ──
    sub.add_parser("login", help="提取并保存 cookies")
    sub.add_parser("check", help="验证 cookies 是否有效")

    # ── 创意 ──
    p = sub.add_parser("list", help="创意列表")
    add_date_args(p); add_page_args(p); add_status_args(p); add_sort_args(p)
    p.add_argument("--plan-id", dest="plan_id", help="只看某计划下的创意")

    p = sub.add_parser("filter", help="按规则筛选创意")
    add_rule_args(p)

    p = sub.add_parser("pause", help="暂停创意")
    add_id_args(p)

    p = sub.add_parser("resume", help="启用/恢复创意")
    add_id_args(p)

    p = sub.add_parser("run", help="一键创意停投流程")
    add_rule_args(p)
    p.add_argument("-y", "--yes", action="store_true")

    p = sub.add_parser("budget", help="修改创意日预算")
    p.add_argument("--id", required=True); p.add_argument("--value", type=float, required=True)

    p = sub.add_parser("bid", help="修改创意出价")
    p.add_argument("--id", required=True); p.add_argument("--value", type=float, required=True)

    # ── 计划 ──
    p = sub.add_parser("plan-list", help="计划列表")
    add_date_args(p); add_page_args(p); add_status_args(p); add_sort_args(p)

    p = sub.add_parser("plan-filter", help="按规则筛选计划")
    add_rule_args(p)

    p = sub.add_parser("plan-pause", help="暂停计划")
    add_id_args(p)

    p = sub.add_parser("plan-resume", help="启用/恢复计划")
    add_id_args(p)

    p = sub.add_parser("plan-run", help="一键计划停投流程")
    add_rule_args(p)
    p.add_argument("-y", "--yes", action="store_true")

    p = sub.add_parser("plan-budget", help="修改计划日预算")
    p.add_argument("--id", required=True); p.add_argument("--value", type=float, required=True)

    p = sub.add_parser("plan-bid", help="修改计划出价")
    p.add_argument("--id", required=True); p.add_argument("--value", type=float, required=True)

    # ── 数据分析 ──
    p = sub.add_parser("summary", help="账户/创意/计划汇总数据")
    add_date_args(p)

    p = sub.add_parser("trend", help="逐日趋势数据")
    add_date_args(p)
    p.add_argument("--days", type=int, default=7, help="近 N 天（默认7）")
    p.add_argument("--level", choices=["account", "plan", "creativity"], default="account")

    p = sub.add_parser("top", help="按指标排行")
    add_date_args(p)
    p.add_argument("--by", default="fee", help="排序字段（默认 fee）")
    p.add_argument("--n", type=int, default=10, help="取前 N 条（默认10）")
    p.add_argument("--asc", action="store_true", help="升序（取最低的）")
    p.add_argument("--level", choices=["creativity", "plan"], default="creativity")

    # ── 导出 ──
    p = sub.add_parser("export", help="导出数据为 CSV/JSON")
    add_date_args(p)
    p.add_argument("--type", choices=["creativity", "plan"], default="creativity")
    p.add_argument("--output", "-o", help="输出文件路径")
    p.add_argument("--format", choices=["csv", "json"], default="csv")
    p.add_argument("--all", action="store_true", help="获取全部页")

    args = parser.parse_args()
    if not hasattr(args, "json"):
        args.json = False

    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "login": cmd_login,
        "check": cmd_check,
        "list": cmd_list,
        "filter": cmd_filter,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "run": cmd_run,
        "budget": cmd_budget,
        "bid": cmd_bid,
        "plan-list": cmd_plan_list,
        "plan-filter": cmd_plan_filter,
        "plan-pause": cmd_plan_pause,
        "plan-resume": cmd_plan_resume,
        "plan-run": cmd_plan_run,
        "plan-budget": cmd_plan_budget,
        "plan-bid": cmd_plan_bid,
        "summary": cmd_summary,
        "trend": cmd_trend,
        "top": cmd_top,
        "export": cmd_export,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
