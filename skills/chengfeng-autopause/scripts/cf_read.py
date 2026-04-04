#!/usr/bin/env python3
"""
cf_read.py - 千帆创意数据读取脚本
用法: python3 cf_read.py [--page 1] [--page-size 20] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
依赖: agent-browser CLI（NAS 上已安装, banana 用户路径）
"""
import subprocess, json, sys, argparse
from datetime import datetime, timedelta

AB = "/home/banana/.hermes/hermes-agent/node_modules/.bin/agent-browser"

def agent_eval(js, timeout=30):
    with open("/tmp/_e.js", "w") as f:
        f.write(js)
    r = subprocess.run(
        f'{AB} eval "$(cat /tmp/_e.js)"',
        shell=True, capture_output=True, text=True, timeout=timeout
    )
    return r.stdout.strip()

def agent_open(url, timeout=30):
    r = subprocess.run(
        f'{AB} open {url}',
        shell=True, capture_output=True, text=True, timeout=timeout
    )
    return r.stdout.strip()

def wait(seconds=4):
    import time
    time.sleep(seconds)

def parse_entry(raw):
    """
    解析 JSON-encoded entry 对象。
    agent-browser eval 返回双重编码的 JSON 字符串，
    所以 json.loads 两次才能得到真正的 dict。
    """
    # 第一次解析：raw 可能是双重编码的 string
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise ValueError(f"无法解析 JSON: {repr(raw[:200])}")

    # 如果还是 string，说明是双重编码，再解析一次
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except (json.JSONDecodeError, TypeError):
            raise ValueError(f"双重 JSON 解析失败: {repr(parsed[:200])}")

    if not isinstance(parsed, dict):
        raise ValueError(f"entry 不是 dict: {type(parsed)}")
    return parsed

def main():
    parser = argparse.ArgumentParser(description="千帆创意数据读取")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    args = parser.parse_args()

    start_date = args.start_date or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    end_date = args.end_date or datetime.now().strftime("%Y-%m-%d")

    print(f"[*] 打开千帆后台...", file=sys.stderr)
    agent_open("https://chengfeng.xiaohongshu.com/cf/ad/manage")
    wait(4)

    # Inject interceptor (增大 res 截断到 50000)
    inject_js = r"""(function(){
      window.__cfLog = [];
      var oxr = XMLHttpRequest.prototype.open;
      XMLHttpRequest.prototype.open = function(m,u){this.__u=u;this.__m=m;return oxr.call(this,m,u);};
      var osr = XMLHttpRequest.prototype.send;
      XMLHttpRequest.prototype.send = function(b){
        if(this.__u && this.__u.match(/\/api\/wind\//)){
          var self = this;
          var entry = {m:this.__m, u:this.__u, b:b||''};
          this.addEventListener('load', function(){
            try { entry.res = self.responseText.slice(0,200000); } catch(e){}
            window.__cfLog.push(entry);
          });
        }
        return osr.call(this,b);
      };
      return 'INJECTED';
    })()"""
    print("[*] 注入拦截器...", file=sys.stderr)
    result = agent_eval(inject_js)
    print(f"    {result}", file=sys.stderr)
    wait(1)

    # Click creativity tab
    click_js = r"""(function(){
      var f=false;
      document.querySelectorAll('*').forEach(function(el){
        if(el.innerText&&el.innerText.trim()==='创意'&&el.offsetWidth>0&&!f){
          el.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));f=true;
        }
      });return f;
    })()"""
    print("[*] 点击创意Tab...", file=sys.stderr)
    click_result = agent_eval(click_js)
    print(f"    {click_result}", file=sys.stderr)
    wait(4)

    # Find creativity/list entry
    find_js = r"""(function(){
      var entries = (window.__cfLog||[]).filter(function(x){return x.u.match(/creativity\/list/);});
      return JSON.stringify(entries[0]||null);
    })()"""
    raw = agent_eval(find_js)
    print(f"[*] API 条目 raw[:80]: {raw[:80]}", file=sys.stderr)

    if not raw or raw == 'null' or raw.strip() == '':
        print("[!] 未找到 creativity/list 请求，请确认已登录且页面已加载", file=sys.stderr)
        sys.exit(1)

    try:
        entry = parse_entry(raw)
    except ValueError as e:
        print(f"[!] 解析失败: {e}", file=sys.stderr)
        sys.exit(1)

    res_raw = entry.get('res', '{}')
    if not res_raw or res_raw == '{}':
        print("[!] 响应体为空（API 可能被截断或返回空）", file=sys.stderr)
        sys.exit(1)

    try:
        res = json.loads(res_raw)
    except json.JSONDecodeError as e:
        print(f"[!] 响应 JSON 解析失败: {e} | 原始: {res_raw[:300]}", file=sys.stderr)
        sys.exit(1)

    if res.get('code') != 0:
        print(f"[!] API 返回错误: {res.get('msg','未知错误')}", file=sys.stderr)
        sys.exit(1)

    data = res.get('data', {})
    rows_raw = data.get('dataList', [])
    total_raw = data.get('totalData', '{}')
    total_page = data.get('totalPage', '?')

    # Parse rows
    parsed_rows = []
    for row in rows_raw:
        try:
            vals = json.loads(row.get('dataValueJson', '{}'))
        except Exception:
            vals = {}
        vals['_id'] = row.get('creativityId', row.get('id', ''))
        vals['_name'] = row.get('name', row.get('title', ''))
        vals['_status'] = row.get('status', '')
        vals['_planId'] = row.get('planId', '')
        vals['_planName'] = row.get('planName', '')
        vals['_noteId'] = row.get('noteId', '')
        parsed_rows.append(vals)

    # Parse total
    try:
        total = json.loads(total_raw) if total_raw else {}
    except Exception:
        total = {}

    # Print human-readable
    print(f"\n{'='*70}")
    print(f"  千帆创意数据  {start_date} ~ {end_date}  第{args.page}页(每页{args.page_size}条)  总{total_page}页")
    print(f"{'='*70}")

    if not parsed_rows:
        print("  (无数据 - 请确认日期范围内有投放记录)")
    else:
        print(f"\n  {'ID':<15} {'名称':<20} {'状态':<6} {'消耗':>10} {'成交笔':>6} {'GMV':>10}")
        print(f"  {'-'*75}")
        for row in parsed_rows:
            cid = str(row.get('_id', ''))[:15]
            name = str(row.get('_name') or '-')[:20]
            status = (row.get('_status') or '-')[:6]
            fee = row.get('fee', '-')
            deal = row.get('dealOrderNum7d', '-')
            gmv = row.get('dealOrderGmv7d', '-')
            print(f"  {cid:<15} {name:<20} {status:<6} {fee:>10} {deal:>6} {gmv:>10}")

    print(f"\n  {'汇总消耗:':>12} {total.get('fee','-')}")
    print(f"  {'汇总成交笔数:':>12} {total.get('dealOrderNum7d','-')}")
    print(f"  {'汇总GMV:':>12} {total.get('dealOrderGmv7d','-')}")
    print(f"  {'requestId:':>12} {res.get('requestId','-')}")
    print(f"{'='*70}\n")

    # Programmatic JSON output (stderr for human, stdout for programmatic)
    output = {
        "requestId": res.get("requestId", ""),
        "totalPage": total_page,
        "total": total,
        "rows": parsed_rows,
        "count": len(parsed_rows),
        "startDate": start_date,
        "endDate": end_date,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False), file=sys.stderr)

if __name__ == "__main__":
    main()
