---
name: chengfeng-autopause
description: 小红书千帆推广（chengfeng.xiaohongshu.com）创意自动停投 Skill。当用户提到"千帆推广"、"乘风计划"、"小红书投流"、"停投创意"、"创意策略"时触发。帮助读取创意投放数据、按配置的标准自动判断要停哪些创意，等用户确认后执行暂停操作。客户交付专用 skill。
---

# 千帆推广 - 创意自动停投 Skill

## 功能概述

读取小红书千帆推广平台的创意数据（通过拦截浏览器内 API 调用获取真实 JSON 数据），
按自然语言配置的停投标准进行判断，输出待停创意列表供确认后执行暂停。

**适用场景：** 客户（谢老师）的投流策略自动化——当创意消耗超过 X 元但零成交时，自动建议或执行停投。

## 核心流程

```
1. 注入拦截器 → 2. 触发 API 调用 → 3. 捕获请求/响应 → 4. 解析数据 → 5. 应用停投标准 → 6. 输出确认列表 → 7. 执行暂停
```

## Step 0：Cookie 直连方式（推荐，无需 Chrome 常开）

**首次使用或 Cookie 过期时，只需运行一次：**

```bash
cd ~/.hermes/skills/chengfeng-autopause/scripts

# 1. 确保 Chrome 已登录千帆，提取并保存 Cookie
python3 cf_cli.py login

# 2. 验证 Cookie 有效
python3 cf_cli.py check
```

**Cookie 保存位置：** `~/.opencli/sessions/chengfeng.cookies.json`

Cookie 一旦保存，后续所有命令直接用，不再需要 Chrome 保持运行：

```bash
# 查看创意列表（近7天）
python3 cf_cli.py list

# 按规则筛选待停创意
python3 cf_cli.py filter --rule "消耗超过10元且成交为0"

# 一键完整停投流程（最常用）
python3 cf_cli.py run --rule "消耗超过10元且成交为0"
python3 cf_cli.py run --rule default --all

# 直接暂停指定创意
python3 cf_cli.py pause --ids 3996550667,3996550668
```

### 预设规则

| 规则名 | 含义 |
|--------|------|
| `default` | 消耗 > 10元 且 7天成交 = 0 |
| `high_spend_no_deal` | 消耗 > 50元 且 7天成交 = 0 |
| `low_roi` | 消耗 > 30元 且 ROI < 0.5 |
| `no_conversion` | 消耗 > 20元 且 展现 > 500 且 成交 = 0 |

也支持自然语言规则：`"消耗超过50元且ROI低于0.3"` / `"消耗超过20元且7天成交笔数为0"`

---

## Step 1：连接浏览器（仅首次提取 Cookie 时需要）

```bash
# 检查已有 chengfeng session 是否存活
~/.hermes/hermes-agent/node_modules/.bin/agent-browser --session chengfeng status
```

如果 session 存在且 Chrome 已登录千帆，直接用。Session 路径：`~/.hermes/hermes-agent/.browser/sessions/chengfeng/`。

### 方式 B：启动新 Chrome + 扫码登录（无已有 session 时）

```bash
# 启动独立 Chrome 配置
'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.openclaw/chrome-cdp-chengfeng"

# 连接
~/.hermes/hermes-agent/node_modules/.bin/agent-browser connect http://127.0.0.1:9222
```

**重要：** 千帆平台只支持短信登录，需要人工扫码。登录一次后 cookies 会持久化，后续无需再登录。

### 验证登录

```javascript
// 打开千帆后台
~/.hermes/hermes-agent/node_modules/.bin/agent-browser open https://chengfeng.xiaohongshu.com/cf/ad/manage

// 验证是否已登录（检查页面是否跳转到登录页）
!(document.body.innerText.includes('登录') || document.body.innerText.includes('sign in'))
```

---

## Step 2：注入 API 拦截器（读取数据的核心）

千帆是 Vue.js SPA，数据通过 XHR/Fetch 请求从后端加载。**不能用 DOM query 读数据**。
必须先向页面注入 JavaScript 拦截器，捕获发往 `/api/wind/` 的 XHR 请求。

### 注入拦截器（每次读取数据前执行）

```javascript
// 保存为 /tmp/cf_inject.js，然后通过 agent-browser eval 执行
window.__cfLog = [];
var oxr = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(m,u){this.__u=u;this.__m=m;return oxr.call(this,m,u);};
var osr = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function(b){
  if(this.__u && this.__u.match(/\/api\/wind\//)){
    var self = this;
    var entry = {m:this.__m, u:this.__u, b:b||''};
    this.addEventListener('load', function(){
      try { entry.res = self.responseText.slice(0,2000); } catch(e){}
      window.__cfLog.push(entry);
    });
  }
  return osr.call(this,b);
};
'INJECTED:' + window.__cfLog.length;
```

执行方式（NAS 上）：
```bash
AB=~/.hermes/hermes-agent/node_modules/.bin/agent-browser
$AB eval "$(cat /tmp/cf_inject.js)"
```

### 触发 API 调用

千帆的创意数据需要切换到「创意」Tab 后才会触发 API 请求：
```javascript
// 点击"创意"tab
var found=false;
document.querySelectorAll('*').forEach(function(el){
  if(el.innerText && el.innerText.trim()==='创意' && el.offsetWidth>0 && !found){
    el.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));found=true;
  }
});
found;
```

等待数据加载：`sleep 4`

### 读取拦截到的 API 数据

```javascript
// 获取创意列表请求的响应（关键 API）
JSON.stringify(window.__cfLog.filter(function(x){return x.u.match(/creativity\/list/)})[0] || null);
// 返回格式: {m:'POST', u:'/api/wind/creativity/list', b:'...请求体...', res:'...响应JSON...'}
```

**已知的 API 端点（2026-04 实测）：**

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/wind/creativity/list` | POST | 创意列表（主要） |
| `/api/wind/creativity_set/list` | POST | 计划列表 |
| `/api/wind/creativity/appealnfo` | POST | 创意申诉信息 |
| `/api/wind/creativity/prefer/audit/list` | POST | 创意审核列表 |
| `/api/wind/data/custom/get?type=3` | GET | 自定义数据 |
| `/api/wind/data/report` | POST | 数据报告 |

---

## Step 3：解析 API 数据

### creativity/list 请求体结构

```json
{
  "page": {"pageIndex": 1, "pageSize": 20},
  "columns": ["fee","impression","click","ctr","acp","cpm","like","comment","collect",
              "follow","share","interaction","cpi","actionButtonClick","actionButtonCtr",
              "screenshot","picSave","searchCmtClick","searchCmtClickCvr",
              "searchCmtAfterReadAvg","searchCmtAfterRead","reservePV",
              "liveSubscribeCnt","liveSubscribeCntCost","liveWatchCnt","liveWatchCntCost",
              "liveWatchDurationAvg","liveFollowCnt","live5sWatchCnt","live5sWatchCntCost",
              "liveCmtCnt","live30sWatchCnt","live30sWatchCntCost",
              "liveDirectGoodsViewNum24h","liveDirectGoodsViewNum24hCost",
              "liveDirectGoodsAddCartNum24h","liveDirectGoodsAddCartNum24hCost",
              "goodsViewNum","goodsViewNumCost","goodsAddCartNum","goodsAddCartNumCost",
              "videoPlayCnt","videoPlay5sCnt","videoPlay5sRate",
              "totalOrderNum7d","totalOrderNum7dCost","totalOrderGmv7d","totalOrderRoi7d",
              "dealOrderNum7d","dealOrderNum7dCost","dealOrderGmv7d","dealOrderRoi7d","dealOrderCvr7d",
              "searchFirstShowImpNum","searchFirstShowClickNum","searchFirstShowFee",
              "searchFirstShowImpRatio","searchFirstShowClickRatio","searchFirstShowFeeRatio",
              "totalOrderNum7dByCvr","totalOrderNum7dCostByCvr","totalOrderGmv7dByCvr","totalOrderRoi7dByCvr",
              "dealOrderNum7dByCvr","dealOrderNum7dCostByCvr","dealOrderGmv7dByCvr","dealOrderRoi7dByCvr",
              "directDealOrderNum24h","directDealOrderNum24hCost","directDealOrderGmv24h","directDealOrderGmv24hRoi",
              "salesDirectPurchaseOrderNum24h","salesDirectPurchaseOrderNum24hCost",
              "salesDirectPurchaseOrderGmv24h","salesDirectPurchaseOrderGmv24hRoi",
              "salesDirectDealOrderNum24h","salesDirectDealOrderNum24hCost",
              "salesDirectDealOrderGmv24h","salesDirectDealOrderGmv24hRoi",
              "liveDirectPurchaseOrderNum24h","liveDirectPurchaseOrderNum24hCost",
              "liveDirectPurchaseOrderGmv24h","liveDirectPurchaseOrderRoi24h",
              "liveDirectDealOrderNum24h","liveDirectDealOrderNum24hCost",
              "liveDirectDealOrderGmv24h","liveDirectDealOrderRoi24h",
              "newSellerGoodsViewNum","newSellerDealOrderNum7d","newSellerDealOrderGmv7d",
              "newSellerLiveDirectDealOrderNum24h","newSellerLiveDirectDealOrderGmv24h"],
  "marketingTargetList": [3, 4, 15],
  "startTime": "2026-04-03",
  "endTime": "2026-04-03"
}
```

### creativity/list 响应结构

```json
{
  "code": 0,
  "success": true,
  "msg": "成功",
  "data": {
    "response": {"success": true, "requestId": "e765de91887c2f4d"},
    "totalData": "{\"fee\":\"0.00\",\"impression\":\"0\",...}",  // JSON 字符串
    "dataList": [
      {
        "creativityId": "3996550667",
        "name": "测试第三条复制",
        "status": "有效",
        "dataValueJson": "{\"fee\":\"72.19\",\"impression\":\"1000\",\"click\":\"50\",\n                          \"ctr\":\"5.0%\",\"dealOrderNum7d\":\"0\",...}"
      }
    ]
  }
}
```

### 关键字段

| 字段 | 含义 |
|------|------|
| `fee` | 近7天消耗金额（元） |
| `dealOrderNum7d` | 7天支付成交笔数（已付款） |
| `totalOrderNum7d` | 7天下单笔数（含未付款） |
| `dealOrderGmv7d` | 7天支付成交金额 |
| `totalOrderGmv7d` | 7天下单金额 |
| `dealOrderRoi7d` | 7天支付ROI |
| `impression` | 展现量 |
| `click` | 点击量 |
| `ctr` | 点击率 |

**"成交"的定义：** 客户说「成交」通常指 `dealOrderNum7d`（已付款），不是 `totalOrderNum7d`（下单）。

---

## Step 4：应用停投标准

**方式 A：JavaScript 硬编码规则（快速，适合自动化）**
```javascript
var targets = rows.filter(function(r){
  var vals = JSON.parse(r.dataValueJson || '{}');
  return vals.fee > 10 && vals.dealOrderNum7d == 0;
});
```

**方式 B：自然语言配置（灵活）**

停投标准由用户在提示词里配置，例如：
```
消耗超过10元且7天成交笔数为0的创意 → 停投
消耗超过50元且ROI低于0.5的创意 → 停投
```
用 LLM 解析标准 → 输出判断代码 → 在 JS 里执行。

---

## Step 5：输出待停创意列表

**必须先给用户确认，不直接自动执行！**

```
待暂停创意列表（共 N 条，合计消耗 X 元）：

| # | 创意ID | 创意名称 | 近7天消耗 | 7天成交 | 7天ROI |
|---|--------|---------|---------|--------|-------|
| 1 | 3996550667 | 测试第三条复制 | 72.19元 | 0 | - |

确认以上 N 条创意要暂停吗？说"确认"我就执行。
```

---

## Step 6：执行暂停

找到目标创意行的「更多」→「暂停」按钮并点击：

```javascript
var rows = document.querySelectorAll('table');
// 找到包含目标ID的行
var found = false;
document.querySelectorAll('*').forEach(function(el){
  if(el.innerText && el.innerText.includes(targetCreativeId) && !found){
    var parent = el.closest('tr') || el.parentElement.closest('tr');
    if(parent){
      var btns = parent.querySelectorAll('button');
      btns.forEach(function(b){
        if(b.innerText.trim() === '更多'){
          b.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
          setTimeout(function(){
            document.querySelectorAll('*').forEach(function(mi){
              if(mi.innerText && mi.innerText.includes('暂停') && mi.offsetWidth>0){
                mi.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));
                found = true;
              }
            });
          },500);
        }
      });
    }
  }
});
found ? '已触发暂停' : '未找到暂停按钮';
```

---

## 已知坑点与应对

| 坑 | 应对 |
|----|------|
| 短信登录无法自动化 | 依赖已有 Chrome 登录态，或人工扫码一次 |
| CDP eval 超时 | 拆解为小步骤，每步单独执行；加 `sleep 2` 等待页面渲染 |
| 下拉框点击无效 | 用 `dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))` |
| 列索引变化（DOM 方式） | 改用 API 拦截方式，不依赖 DOM 列位置 |
| Cookie 过期 | 重新扫码登录千帆平台 |
| 拦截器返回空 | 确认 `window.__cfLog` 长度 > 0；页面需登录且切换到正确 Tab |

---

## 快速执行脚本（复制使用）

### 读取创意数据完整流程

```bash
AB=~/.hermes/hermes-agent/node_modules/.bin/agent-browser

# 1. 打开页面
$AB open https://chengfeng.xiaohongshu.com/cf/ad/manage
sleep 4

# 2. 注入拦截器
$AB eval "$(cat /tmp/cf_inject.js)"
sleep 1

# 3. 点击创意 tab
$AB eval "var f=false;document.querySelectorAll('*').forEach(function(el){if(el.innerText&&el.innerText.trim()==='创意'&&el.offsetWidth>0&&!f){el.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));f=true;}});f;"
sleep 4

# 4. 获取创意列表响应
$AB eval "JSON.stringify((window.__cfLog||[]).filter(function(x){return x.u.match(/creativity\/list/)}).map(function(x){return {m:x.m,u:x.u,b:x.b,res:x.res};})[0]||null)"
```

### 执行文件（scripts/cf_read.py）

`scripts/cf_read.py` 脚本封装了上述流程，在已登录的浏览器 session 中：
1. 注入拦截器
2. 触发创意 tab API 调用
3. 解析响应 JSON，输出结构化数据

用法：
```bash
python3 scripts/cf_read.py [--page 1] [--page-size 20] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
```

---

## 依赖

- `agent-browser` CLI（必须）
- Chrome CDP Session（必须，千帆平台账号已登录）

## 输出规范

Skill 执行完成后必须输出：
1. 读取到的创意总数
2. 符合停投标准的创意数量
3. 待暂停创意列表（含创意ID、名称、消耗、成交数据）
4. 明确要求用户确认后才执行暂停操作
