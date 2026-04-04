#!/usr/bin/env python3
"""
cf_export.py - 千帆数据导出工具

支持格式：CSV、JSON
支持层级：创意（creativity）、计划（plan）

用法（作为模块）：
    from cf_export import export_csv, export_json

用法（独立运行）：
    python3 cf_export.py --input rows.json --output cf_data.csv
    python3 cf_export.py --input rows.json --output cf_data.json --format json
"""

import csv
import json
import os
import sys
from datetime import datetime


# ─── 导出字段定义 ────────────────────────────────────────────────────────────

# 创意层导出列（中文 header → 字段名）
CREATIVITY_EXPORT_COLUMNS = [
    ("创意ID",       "_id"),
    ("创意名称",      "_name"),
    ("状态",         "_status"),
    ("计划ID",       "_planId"),
    ("计划名称",      "_planName"),
    ("营销目标",      "_marketingTarget"),
    ("日预算",       "_budget"),
    ("出价",         "_bid"),
    # 核心消耗
    ("近7天消耗(元)", "fee"),
    ("展现量",       "impression"),
    ("点击量",       "click"),
    ("点击率",       "ctr"),
    ("CPM",         "cpm"),
    ("CPI",         "cpi"),
    # 互动
    ("互动量",       "interaction"),
    ("点赞",         "like"),
    ("评论",         "comment"),
    ("收藏",         "collect"),
    ("关注",         "follow"),
    ("分享",         "share"),
    # 视频
    ("视频播放量",    "videoPlayCnt"),
    ("视频5s播放量",  "videoPlay5sCnt"),
    ("视频5s播放率",  "videoPlay5sRate"),
    # 商品
    ("商品浏览量",    "goodsViewNum"),
    ("商品浏览成本",  "goodsViewNumCost"),
    ("加购量",       "goodsAddCartNum"),
    ("加购成本",     "goodsAddCartNumCost"),
    # 成交（7天付款）
    ("7天付款成交笔", "dealOrderNum7d"),
    ("7天付款成交成本","dealOrderNum7dCost"),
    ("7天付款GMV",   "dealOrderGmv7d"),
    ("7天付款ROI",   "dealOrderRoi7d"),
    ("7天付款转化率", "dealOrderCvr7d"),
    # 成交（7天下单）
    ("7天下单笔",    "totalOrderNum7d"),
    ("7天下单成本",  "totalOrderNum7dCost"),
    ("7天下单GMV",   "totalOrderGmv7d"),
    ("7天下单ROI",   "totalOrderRoi7d"),
    # 直接成交（24h）
    ("24h直接付款笔", "directDealOrderNum24h"),
    ("24h直接付款成本","directDealOrderNum24hCost"),
    ("24h直接付款GMV","directDealOrderGmv24h"),
    ("24h直接付款ROI","directDealOrderGmv24hRoi"),
    # 直播
    ("直播观看量",    "liveWatchCnt"),
    ("直播观看成本",  "liveWatchCntCost"),
    ("直播关注量",    "liveFollowCnt"),
    ("直播5s观看",   "live5sWatchCnt"),
    ("直播5s观看成本","live5sWatchCntCost"),
    ("直播直接成交",  "liveDirectDealOrderNum24h"),
    ("直播直接成交成本","liveDirectDealOrderNum24hCost"),
    ("直播直接GMV",  "liveDirectDealOrderGmv24h"),
    ("直播直接ROI",  "liveDirectDealOrderRoi24h"),
    # 搜索
    ("搜索首屏展现",  "searchFirstShowImpNum"),
    ("搜索首屏点击",  "searchFirstShowClickNum"),
    ("搜索首屏消耗",  "searchFirstShowFee"),
    ("搜索评论互动",  "searchCmtClick"),
]

# 计划层导出列
PLAN_EXPORT_COLUMNS = [
    ("计划ID",       "_id"),
    ("计划名称",      "_name"),
    ("状态",         "_status"),
    ("营销目标",      "_marketingTarget"),
    ("日预算",       "_budget"),
    ("出价",         "_bid"),
    ("创意数量",      "_creativityCount"),
    # 核心指标（与创意层相同）
    ("近7天消耗(元)", "fee"),
    ("展现量",       "impression"),
    ("点击量",       "click"),
    ("点击率",       "ctr"),
    ("CPM",         "cpm"),
    ("互动量",       "interaction"),
    ("7天付款成交笔", "dealOrderNum7d"),
    ("7天付款GMV",   "dealOrderGmv7d"),
    ("7天付款ROI",   "dealOrderRoi7d"),
    ("7天下单笔",    "totalOrderNum7d"),
    ("7天下单GMV",   "totalOrderGmv7d"),
    ("24h直接付款笔", "directDealOrderNum24h"),
    ("24h直接付款GMV","directDealOrderGmv24h"),
    ("24h直接付款ROI","directDealOrderGmv24hRoi"),
    ("直播观看量",    "liveWatchCnt"),
    ("直播直接成交",  "liveDirectDealOrderNum24h"),
    ("直播直接GMV",  "liveDirectDealOrderGmv24h"),
]


# ─── 导出函数 ────────────────────────────────────────────────────────────────

def export_csv(rows: list, output_path: str, row_type: str = "creativity",
               columns: list = None) -> str:
    """
    导出创意或计划数据为 CSV。
    columns: [(header, field), ...] 自定义列，None 则用默认
    返回写入的文件路径。
    """
    if not rows:
        print("[!] 无数据，跳过导出", file=sys.stderr)
        return output_path

    cols = columns or (PLAN_EXPORT_COLUMNS if row_type == "plan" else CREATIVITY_EXPORT_COLUMNS)

    # 确保目录存在
    dirpath = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(dirpath, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        # 写表头
        writer.writerow([col[0] for col in cols])
        # 写数据
        for row in rows:
            writer.writerow([_get_val(row, col[1]) for col in cols])

    print(f"[✓] CSV 导出完成: {output_path}  ({len(rows)} 条)", file=sys.stderr)
    return output_path


def export_json(rows: list, output_path: str, meta: dict = None) -> str:
    """导出为 JSON 文件。"""
    if not rows:
        print("[!] 无数据，跳过导出", file=sys.stderr)
        return output_path

    dirpath = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(dirpath, exist_ok=True)

    out = {
        "exported_at": datetime.now().isoformat(),
        "count": len(rows),
        "rows": rows,
    }
    if meta:
        out.update(meta)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"[✓] JSON 导出完成: {output_path}  ({len(rows)} 条)", file=sys.stderr)
    return output_path


def export_summary_csv(rows: list, output_path: str) -> str:
    """
    导出精简汇总版本（适合发给客户看）：只含核心指标。
    """
    summary_cols = [
        ("创意/计划ID", "_id"),
        ("名称",        "_name"),
        ("状态",        "_status"),
        ("消耗(元)",    "fee"),
        ("展现量",      "impression"),
        ("点击量",      "click"),
        ("点击率",      "ctr"),
        ("7天成交笔",   "dealOrderNum7d"),
        ("7天GMV",     "dealOrderGmv7d"),
        ("7天ROI",     "dealOrderRoi7d"),
        ("24h直接成交", "directDealOrderNum24h"),
        ("24h直接GMV",  "directDealOrderGmv24h"),
    ]
    return export_csv(rows, output_path, columns=summary_cols)


def _get_val(row: dict, field: str) -> str:
    """从 row 中取字段值，处理 None / '-' / 特殊字符。"""
    val = row.get(field, "")
    if val is None or val == "-":
        return ""
    return str(val)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="千帆数据导出工具")
    parser.add_argument("--input", required=True, help="输入 JSON 文件（rows 数组）")
    parser.add_argument("--output", "-o", default="cf_export.csv", help="输出文件路径")
    parser.add_argument("--format", choices=["csv", "json", "summary"], default="csv",
                        help="导出格式：csv / json / summary（精简版 CSV）")
    parser.add_argument("--type", choices=["creativity", "plan"], default="creativity",
                        dest="row_type", help="数据类型")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    rows = data.get("rows") or data.get("targets") or (data if isinstance(data, list) else [])
    if not rows:
        print("[!] 输入文件中未找到 rows 数组", file=sys.stderr)
        sys.exit(1)

    print(f"[*] 读取 {len(rows)} 条，导出为 {args.format.upper()}...", file=sys.stderr)

    if args.format == "json":
        export_json(rows, args.output)
    elif args.format == "summary":
        export_summary_csv(rows, args.output)
    else:
        export_csv(rows, args.output, row_type=args.row_type)
