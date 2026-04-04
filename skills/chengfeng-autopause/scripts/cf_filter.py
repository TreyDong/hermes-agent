#!/usr/bin/env python3
"""
cf_filter.py - 千帆创意/计划 停投规则解析与过滤

支持：
  - 自然语言规则（中文）
  - 预设规则字典
  - 数值排序（top-N / bottom-N）
  - 状态过滤
  - 多维度条件 AND 组合

字段映射（dataValueJson 字段名 ↔ 中文别名）:
  消耗/费用/花费       → fee
  成交/成交笔数        → dealOrderNum7d
  GMV/成交金额         → dealOrderGmv7d
  ROI/投产比           → dealOrderRoi7d
  下单/下单笔数        → totalOrderNum7d
  下单GMV              → totalOrderGmv7d
  展现/曝光            → impression
  点击/点击量          → click
  点击率/CTR           → ctr
  CPM                  → cpm
  CPI                  → cpi
  互动/互动量          → interaction
  点赞/like            → like
  评论/comment         → comment
  收藏/collect         → collect
  关注/follow          → follow
  分享/share           → share
  预算                 → _budget
  出价/bid             → _bid
  创意数               → _creativityCount（计划层）
"""

import re
import json
import sys
from typing import Callable


# ─── 字段别名映射 ─────────────────────────────────────────────────────────────

FIELD_ALIASES: dict[str, str] = {
    # 消耗
    "消耗": "fee", "费用": "fee", "花费": "fee", "支出": "fee", "花了": "fee",
    # 成交笔数（已付款）——"成交"默认映射到已付款
    "成交": "dealOrderNum7d", "成交笔数": "dealOrderNum7d",
    "成交笔": "dealOrderNum7d", "付款成交": "dealOrderNum7d",
    "已付款成交": "dealOrderNum7d", "成交单数": "dealOrderNum7d",
    "7天成交": "dealOrderNum7d", "七天成交": "dealOrderNum7d",
    # 成交金额 / GMV
    "GMV": "dealOrderGmv7d", "gmv": "dealOrderGmv7d",
    "成交金额": "dealOrderGmv7d", "付款金额": "dealOrderGmv7d",
    "成交额": "dealOrderGmv7d", "7天GMV": "dealOrderGmv7d", "七天GMV": "dealOrderGmv7d",
    # ROI
    "ROI": "dealOrderRoi7d", "roi": "dealOrderRoi7d",
    "投产比": "dealOrderRoi7d", "回报率": "dealOrderRoi7d",
    "7天ROI": "dealOrderRoi7d", "七天ROI": "dealOrderRoi7d",
    # 下单（含未付款）
    "下单": "totalOrderNum7d", "下单笔数": "totalOrderNum7d",
    "下单数": "totalOrderNum7d", "下单量": "totalOrderNum7d",
    "下单GMV": "totalOrderGmv7d", "下单金额": "totalOrderGmv7d",
    # 展现 / 曝光
    "展现": "impression", "曝光": "impression", "展示": "impression",
    "展现量": "impression", "曝光量": "impression", "impression": "impression",
    # 点击
    "点击": "click", "点击量": "click", "点击数": "click", "click": "click",
    # 点击率
    "点击率": "ctr", "CTR": "ctr", "ctr": "ctr",
    # CPM / CPI
    "CPM": "cpm", "cpm": "cpm", "千次曝光成本": "cpm",
    "CPI": "cpi", "cpi": "cpi",
    # 互动
    "互动": "interaction", "互动量": "interaction", "互动数": "interaction",
    # 社交互动
    "点赞": "like", "like": "like",
    "评论": "comment", "comment": "comment",
    "收藏": "collect", "collect": "collect",
    "关注": "follow", "follow": "follow",
    "分享": "share", "share": "share",
    # 预算 / 出价
    "预算": "_budget", "日预算": "_budget",
    "出价": "_bid", "bid": "_bid",
    # 计划专属
    "创意数": "_creativityCount", "创意数量": "_creativityCount",
    # 直播
    "直播观看": "liveWatchCnt", "直播观看量": "liveWatchCnt",
    "直播成交": "liveDirectDealOrderNum24h",
    "直播ROI": "liveDirectDealOrderRoi24h",
}

# 操作符关键词 → Python 操作符（按优先级从长到短匹配）
OPERATOR_PATTERNS: list[tuple] = [
    (r"大于等于|>=|≥|不低于|至少|不少于", ">="),
    (r"小于等于|<=|≤|不高于|最多|至多|不超过", "<="),
    (r"大于|超过|高于|>|多于|超出|超了", ">"),
    (r"小于|低于|不到|<|少于|未达到|不足|没到", "<"),
    (r"等于|==|为0|=0|是0|零笔|零单|为零|没有成交|无成交|零成交", "=="),
    (r"不等于|!=|不是|非零|有成交", "!="),
]


# ─── 规则结构 ────────────────────────────────────────────────────────────────

class Rule:
    def __init__(self, field: str, op: str, value: float, description: str = ""):
        self.field = field
        self.op = op
        self.value = value
        self.description = description

    def matches(self, row: dict) -> bool:
        raw = row.get(self.field)
        if raw is None or raw == "" or raw == "-":
            # 零值特殊处理：字段缺失时，"== 0" 视为满足（消耗为0也算零成交）
            if self.op == "==" and self.value == 0.0:
                return True
            return False
        try:
            val = float(str(raw).replace("%", "").replace(",", "").replace("元", "").strip())
        except (ValueError, TypeError):
            return False
        ops = {
            ">": val > self.value,
            ">=": val >= self.value,
            "<": val < self.value,
            "<=": val <= self.value,
            "==": val == self.value,
            "!=": val != self.value,
        }
        return ops.get(self.op, False)

    def __repr__(self):
        return f"Rule({self.field} {self.op} {self.value})"


class RuleSet:
    """多条规则的 AND 组合。"""
    def __init__(self, rules: list, description: str = "", mode: str = "AND"):
        self.rules = rules
        self.description = description
        self.mode = mode  # 'AND' | 'OR'

    def matches(self, row: dict) -> bool:
        if self.mode == "OR":
            return any(r.matches(row) for r in self.rules)
        return all(r.matches(row) for r in self.rules)

    def __repr__(self):
        sep = f" {self.mode} "
        return f"RuleSet({sep.join(str(r) for r in self.rules)})"


# ─── 预设规则 ────────────────────────────────────────────────────────────────

PRESET_RULES: dict[str, RuleSet] = {
    "default": RuleSet([
        Rule("fee", ">", 10.0, "消耗 > 10元"),
        Rule("dealOrderNum7d", "==", 0.0, "7天成交 = 0"),
    ], description="消耗>10元 且 7天成交=0（默认）"),

    "high_spend_no_deal": RuleSet([
        Rule("fee", ">", 50.0, "消耗 > 50元"),
        Rule("dealOrderNum7d", "==", 0.0, "7天成交 = 0"),
    ], description="消耗>50元 且 7天成交=0"),

    "low_roi": RuleSet([
        Rule("fee", ">", 30.0, "消耗 > 30元"),
        Rule("dealOrderRoi7d", "<", 0.5, "7天ROI < 0.5"),
    ], description="消耗>30元 且 ROI<0.5"),

    "no_conversion": RuleSet([
        Rule("fee", ">", 20.0, "消耗 > 20元"),
        Rule("dealOrderNum7d", "==", 0.0, "7天成交 = 0"),
        Rule("impression", ">", 500.0, "展现 > 500"),
    ], description="消耗>20元 且 展现>500 且 零成交"),

    "low_ctr": RuleSet([
        Rule("impression", ">", 1000.0, "展现 > 1000"),
        Rule("ctr", "<", 1.0, "点击率 < 1%"),
    ], description="展现>1000 且 点击率<1%（低点击率）"),

    "high_cpi": RuleSet([
        Rule("fee", ">", 50.0, "消耗 > 50元"),
        Rule("cpi", ">", 30.0, "CPI > 30元"),
    ], description="消耗>50元 且 CPI>30元（获客成本高）"),

    "active_only": RuleSet([
        Rule("fee", ">", 0.0, "有消耗"),
    ], description="近期有消耗的创意/计划"),

    "zero_impression": RuleSet([
        Rule("impression", "==", 0.0, "展现 = 0"),
    ], description="零展现（可能被限流或审核中）"),
}


# ─── 自然语言解析 ────────────────────────────────────────────────────────────

def _resolve_field(text: str) -> str | None:
    # 按别名长度降序匹配（避免"成交金额"被"成交"先匹配到）
    for alias in sorted(FIELD_ALIASES, key=len, reverse=True):
        if alias in text:
            return FIELD_ALIASES[alias]
    return None


def _resolve_operator(text: str) -> str | None:
    for pattern, op in OPERATOR_PATTERNS:
        if re.search(pattern, text):
            return op
    return None


def _extract_number(text: str) -> float | None:
    m = re.search(r"(\d+\.?\d*)", text)
    return float(m.group(1)) if m else None


def parse_natural_rule(text: str) -> RuleSet | None:
    """
    解析自然语言规则字符串，返回 RuleSet。
    支持「且」「并且」「,」「、」分隔多条条件。
    """
    # 分割条件
    clauses = re.split(r"[且并且,、and\s]+(?=(?:消耗|成交|GMV|ROI|展现|点击|曝光|下单|预算|创意|直播))", text, flags=re.IGNORECASE)
    if len(clauses) <= 1:
        clauses = re.split(r"[且并且]+", text)

    rules = []
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue

        field = _resolve_field(clause)
        if not field:
            print(f"  [!] 无法识别字段: '{clause}'，跳过", file=sys.stderr)
            continue

        op = _resolve_operator(clause)
        if not op:
            if re.search(r"为0|=0|零|没有|无|为零|零笔|零单", clause):
                op = "=="
            else:
                print(f"  [!] 无法识别操作符: '{clause}'，跳过", file=sys.stderr)
                continue

        value = _extract_number(clause)
        if value is None:
            if op == "==" or re.search(r"为0|=0|零|没有|无|为零", clause):
                value = 0.0
            else:
                print(f"  [!] 无法提取数值: '{clause}'，跳过", file=sys.stderr)
                continue

        rules.append(Rule(field, op, value, description=clause.strip()))

    if not rules:
        return None
    return RuleSet(rules, description=text)


# ─── 过滤与排序 ──────────────────────────────────────────────────────────────

def apply_status_filter(rows: list,
                        include_paused: bool = False,
                        only_paused: bool = False) -> list:
    """
    过滤行的状态。
    include_paused=True  → 包含已暂停的
    only_paused=True     → 只看已暂停的
    """
    pause_statuses = {"暂停", "PAUSE", "pause", "已暂停", "停止"}
    if only_paused:
        return [r for r in rows if r.get("_status", "") in pause_statuses]
    if include_paused:
        return rows
    return [r for r in rows if r.get("_status", "") not in pause_statuses]


def apply_rules(rows: list, ruleset: RuleSet) -> list:
    """对行列表应用 RuleSet，返回匹配的行。"""
    return [row for row in rows if ruleset.matches(row)]


def sort_rows(rows: list, field: str, ascending: bool = False) -> list:
    """按指定字段排序。"""
    def key_fn(r):
        val = r.get(field, None)
        if val is None or val == "" or val == "-":
            return float("-inf") if not ascending else float("inf")
        try:
            return float(str(val).replace("%", "").replace(",", "").replace("元", "").strip())
        except (ValueError, TypeError):
            return float("-inf") if not ascending else float("inf")
    return sorted(rows, key=key_fn, reverse=not ascending)


def top_n(rows: list, field: str, n: int, ascending: bool = False) -> list:
    """取排序后前 N 条。ascending=True 取最小的 N 条（如 ROI 最低的）。"""
    return sort_rows(rows, field, ascending=ascending)[:n]


# ─── 格式化输出 ──────────────────────────────────────────────────────────────

def format_pause_list(rows: list, rule_desc: str = "", action: str = "暂停") -> str:
    if not rows:
        return "（无符合条件的创意/计划）"

    total_fee = 0.0
    for r in rows:
        try:
            total_fee += float(str(r.get("fee", 0) or 0).replace(",", ""))
        except (ValueError, TypeError):
            pass

    row_type = "计划" if rows[0].get("_type") == "plan" else "创意"
    lines = [
        f"待{action}{row_type}列表（共 {len(rows)} 条，合计消耗约 {total_fee:.2f} 元）",
        f"停投规则：{rule_desc}" if rule_desc else "",
        "",
        f"| # | {row_type}ID | {row_type}名称 | 近7天消耗 | 7天成交 | 7天ROI |",
        f"|---|---------|---------|---------|--------|-------|",
    ]
    for i, r in enumerate(rows, 1):
        rid = r.get("_id", "")
        name = (r.get("_name") or "")[:25]
        fee = r.get("fee", "-")
        deal = r.get("dealOrderNum7d", "-")
        roi = r.get("dealOrderRoi7d", "-")
        lines.append(f"| {i} | {rid} | {name} | {fee}元 | {deal} | {roi} |")

    lines.append("")
    lines.append(f"确认以上 {len(rows)} 条{row_type}要{action}吗？说「确认」我就执行。")
    return "\n".join(l for l in lines if l is not None)


def format_top_list(rows: list, field: str, n: int, title: str = "") -> str:
    if not rows:
        return "（无数据）"
    lines = [title or f"Top {n}（按 {field} 排序）", ""]
    for i, r in enumerate(rows, 1):
        rid = r.get("_id", "")
        name = (r.get("_name") or "")[:20]
        val = r.get(field, "-")
        fee = r.get("fee", "-")
        lines.append(f"  {i:>3}. [{rid}] {name} | {field}: {val} | 消耗: {fee}元")
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="千帆停投规则测试（单独使用）")
    parser.add_argument("--rule", default="default",
                        help="规则名或自然语言，如: '消耗超过10元且成交为0'")
    parser.add_argument("--sort", help="排序字段，如: fee / dealOrderNum7d")
    parser.add_argument("--top", type=int, help="只取前 N 条")
    parser.add_argument("--input", help="JSON 文件（cf_http list 的输出）")
    parser.add_argument("--row-type", default="creativity", choices=["creativity", "plan"])
    parser.add_argument("--include-paused", action="store_true")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
        rows = data.get("rows", [])
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("用法: python3 cf_filter.py --rule '消耗超过10元且成交为0' --input rows.json")
            sys.exit(0)
        data = json.loads(raw)
        rows = data.get("rows", [])

    # 标记类型
    for r in rows:
        if "_type" not in r:
            r["_type"] = args.row_type

    # 状态过滤
    active = apply_status_filter(rows, include_paused=args.include_paused)

    # 规则过滤
    if args.rule in PRESET_RULES:
        ruleset = PRESET_RULES[args.rule]
    else:
        ruleset = parse_natural_rule(args.rule)
        if not ruleset:
            print(f"[!] 规则解析失败: {args.rule}", file=sys.stderr)
            sys.exit(1)

    targets = apply_rules(active, ruleset)

    # 排序
    if args.sort:
        targets = sort_rows(targets, args.sort)
    if args.top:
        targets = targets[:args.top]

    print(format_pause_list(targets, ruleset.description))
    print(json.dumps({
        "targets": targets,
        "count": len(targets),
        "rule": ruleset.description,
    }, indent=2, ensure_ascii=False))
