---
name: greengrid-video-pipeline
description: 亿电通 GreenGrid 官网宣传视频生成与 Discord 上传全流程 — 踩坑记录
triggers:
  - GreenGrid 视频生成
  - 亿电通 官网视频
  - Discord 视频上传
  - Ark API ModelNotOpen
  - mmx 视频生成
  - Hailuo 视频
  - 旁白优先 视频制作
  - 中文配音 视频
  - 中文字幕 烧录
---

# 亿电通宣传视频生成流程

## 踩坑记录（必读）

### 坑1：ARK API Key 找错了（已解决，但仍有坑）
- `~/.hermes/.env` 里的 `ARK_API_KEY`（db4406...）**仅供 LLM 使用**，视频 API 用会报 `AuthenticationError: The API key doesn't exist`
- **正确 key**：`a993f34b-b093-4ff0-b712-0e51cc030a6f`（用户直接提供的火山方舟账号 key）
- **症状**：能读取历史任务列表，但创建新任务永远 401 → **换 key 就好了**
- **注意**：这个 key 在控制台可查视频模型用量，但无法通过 API 查询配额

### 坑1b：Safe Experience Mode 限制（2026-04-12 新增！）
- **症状**：`SetLimitExceeded: Your account has reached the set inference limit for the [doubao-seedance-2-0] model, and the model service has been paused`
- 同时触发于 Seedance 2.0 和 1.5pro，说明是账户级别限制
- **解决**：用户必须手动操作：登录 ark.cn-beijing.volces.com → 模型激活 → 关闭目标模型的 Safe Experience Mode
- **无法绕过**，必须用户操作，不能靠换 key/换模型解决

### 坑2：Ken Burns scale 黑边问题（核心！）
`scale=1280:720:force_original_aspect_ratio=increase` 会**保持原比例加黑边**，导致画面内容只有一小块，视觉上看起来是纯色背景。

**正确方案：scale 填满后再 crop**
```python
def scale_crop_fill(src_w, src_h, target_w=1280, target_h=720, zoom=1.0):
    """zoom 放大然后 crop 填充，无黑边"""
    sw, sh = int(src_w * zoom), int(src_h * zoom)
    r_src = sw / sh
    r_dst = target_w / target_h
    if r_src > r_dst:
        new_w = int(sw * target_h / sh)
        x_crop = (new_w - target_w) // 2
        return f"scale={new_w}:{target_h},crop={target_w}:{target_h}:{x_crop}:0,setsar=1"
    else:
        new_h = int(sh * target_w / sw)
        y_crop = (new_h - target_h) // 2
        return f"scale={target_w}:{new_h},crop={target_w}:{target_h}:0:{y_crop},setsar=1"
```

**overlay 只接受2个输入**：Ken Burns 三档 zoom 串联要这样写：
```
[k0][k1]overlay=0:0:enable='between(t,2.3,4.6)'[tmp];
[tmp][k2]overlay=0:0:enable='gt(t,4.6)'[bg]
```

### 坑3：Discord CLI 发文件 400 错误
- `discord-cli msg send --file` 报 `API Error 400: The request body contains invalid JSON`
- 纯文本没问题，文件就崩 → CLI 的 multipart 编码有 bug
- **解法**：绕开 CLI，直接用 `requests.post` 上传

### 坑4：Discord 附件 8MB 上限
- 视频合成后 11MB，Discord 返回 `413 Request entity too large`
- **解法**：ffmpeg 压缩
  ```bash
  ffmpeg -y -i input.mp4 \
    -c:v libx264 -preset fast -crf 26 -maxrate 1.5M -bufsize 3M \
    -c:a aac -b:a 64k \
    -movflags +faststart \
    output_compressed.mp4
  ```
  可压到 5-6MB，画质损失可接受

## 工具优先级（重要原则！）
**用户明确说用 Seedance 2.0，就用 Seedance 2.0，不要自作主张换成 MiniMax/Hailuo！**
- ✅ Seedance 2.0 (`doubao-seedance-2-0-260128`) — 用户指定，优先用
- ⚠️ Seedance 1.5pro (`doubao-seedance-1-5-pro-251215`) — 2.0 配额不足时的备选
- ❌ MiniMax/Hailuo — 用户未要求时不应主动使用
- ❌ Remotion — 仅当 AI 视频配额全部耗尽时的最后手段

### 核心问题：crop-fill 替代 force_original_aspect_ratio=increase

**错误做法（v1-v4 的 bug 根源）：**
```bash
ffmpeg ... -vf "scale=1280:720:force_original_aspect_ratio=increase"
# 问题：保持原比例缩放，会加黑边，实际画面内容只剩一小块
```

**正确做法：用 scale 填满，再用 crop 切回来**
```python
def crop_for_fill(iw, ih, target_w=1280, target_h=720, zoom=1.0):
    """短边填满目标尺寸，长边溢出后中心 crop。无黑边。"""
    sw = int(iw * zoom)
    sh = int(ih * zoom)
    r_src = sw / sh
    r_dst = target_w / target_h
    if r_src > r_dst:
        # 更扁：scale 到目标高度，宽度溢出，crop 宽度
        new_sh = target_h
        new_sw = int(sw * target_h / sh)
        cx = (new_sw - target_w) // 2; cy = 0
    else:
        # 更高：scale 到目标宽度，高度溢出，crop 高度
        new_sw = target_w
        new_sh = int(sh * target_w / sw)
        cx = 0; cy = (new_sh - target_h) // 2
    return f"scale={new_sw}:{new_sh},crop={target_w}:{target_h}:{cx}:{cy},setsar=1"
```

**注意：crop 参数不能用 ffmpeg 变量（iw/ih），要在 Python 端算好具体像素值再传给 ffmpeg。**

### 场景截图尺寸（易电通官网）
| 截图 | 尺寸 | 比例 |
|------|------|------|
| scene1_hero | 1280×560 | 非16:9 |
| scene2_products | 1280×720 | 16:9 |
| scene3_scm | 1280×720 | 16:9 |
| scene4_suppliers | 1280×720 | 16:9 |

scene1 特别短，需要 crop-for-fill 才能无黑边填满 1280×720。

### Footer Bar 设计（优于中间叠加）
- **中间叠加（v1-v5）：** 渐变遮罩盖在截图中间，严重遮挡主内容，视觉差
- **Footer bar（v6+）：** 底部留 88px 黑色条 + 金色分隔线 + 文字，截图全屏不受影响
```python
FOOTER_Y = 632  # y=632 开始，h=88 高的黑条
fc = (
    f"[bg]drawbox=x=0:y={FOOTER_Y}:w={W}:h=88:color=black@0.82:t=fill[fb];"
    f"[fb]drawbox=x=0:y={FOOTER_Y}:w={W}:h=2:color=0xf0c040@0.9:t=fill[fbt];"
    f"[fbt]drawtext=text='{title}':fontfile={FONT}:fontcolor=0xf0c040:fontsize=36:"
    f"borderw=2:bordercolor=black@0.5:x={x_t}:y={FOOTER_Y+10}[ttxt];"
    f"[ttxt]drawtext=text='{subtitle}':fontfile={FONT}:fontcolor=0xd0dff0:fontsize=18:"
    f"x={x_s}:y={FOOTER_Y+52}"
)
```

### Ken Burns 实现（3档 crop 区域偏移）
```python
offsets = [(0, 0), (15, 8), (28, 15)]  # 三档 zoom 下的 crop 偏移 (dcx, dcy)
# 每档 ~2.3s，overlay 拼接
fc_kb = (
    f"[k0][k1]overlay=0:0:enable='between(t,2.3,4.6)'[tmp];"
    f"[tmp][k2]overlay=0:0:enable='gt(t,4.6)'[bg]"
)
```

---

## 完整流程（mmx CLI 版 — 2026-04-12 更新）

### 原则：旁白优先工作流
**错误顺序**：先生成视频 → 再配音 → 音画不同步
**正确顺序**：写旁白文案 → 生成TTS → 测量音频时长 → 按时长生成视频 → 合并 → 烧录字幕

### 1. 写旁白文案并生成 TTS
```bash
mkdir -p /tmp/greengrid_assets/sections
VOICE="Chinese (Mandarin)_Male_Announcer"  # 男声播音员

mmx speech synthesize --region cn --voice "$VOICE" \
  --text "第一段文字..." --non-interactive --output sections/s1.mp3
# 每个音频片段单独生成，再合并
```

### 2. 合并音频 + 测量总时长
```bash
cat > list.txt << 'EOF'
file 's1.mp3'
file 's2.mp3'
file 's3.mp3'
file 's4.mp3'
EOF
ffmpeg -y -f concat -safe 0 -i list.txt -c copy full_narration.mp3
# 用 ffprobe 测量每段和总时长，作为视频生成目标时长
```

### 3. 提交视频生成任务（每段对应音频片段）
```bash
# 关键：用 --no-wait 异步提交，避免等待超时
# 注意：Hailuo-2.3 每段默认约6秒（实测），可能短于目标音频时长
mmx video generate \
  --model MiniMax-Hailuo-2.3 \
  --first-frame "/path/to/first_frame.jpg" \
  --prompt "英文描述..." \
  --no-wait --quiet
# 返回 {"taskId":"123456789"}
```

### 4. 监控任务 + 下载（注意配额！）
```bash
# 轮询状态
mmx video task get --task-id <TASK_ID> --output json

# 下载（--download 参数有时不生效，用这个！）
mmx video download --file-id <FILE_ID> --out output.mp4 --quiet
# FILE_ID 从 task get 输出中获取

# 查看剩余配额
mmx quota show | python3 -c "
import sys,json; d=json.load(sys.stdin)
for m in d['model_remains']:
    if 'Hailuo' in m['model_name']:
        rem = m['current_interval_total_count']-m['current_interval_usage_count']
        print(f'{m[\"model_name\"]}: {rem}/{m[\"current_interval_total_count\"]}')
"
```

### 5. 视频延伸（当 AI 视频短于目标音频时长）
```bash
# Hailuo 实际产出约5.9秒/段，需要延伸到音频长度
ffmpeg -y -stream_loop -1 -i input_raw.mp4 -t 13.9 \
  -vf "setpts=PTS-STARTPTS" \
  -c:v libx264 -preset fast -crf 23 -r 30 -an output_extended.mp4
```

### 6. 合并 + 烧录中文字幕
```python
# 中文配音需要文泉驿字体
FONT = "/usr/share/fonts/truetype/wenquanyi/WenQuanYiZenHei.ttf"
FONT_SIZE = 56

subs = [
    (0.0, 3.0, "亿电通，让全球电力设备贸易更简单"),
    (3.0, 6.0, "我们专注智能电网与新能源领域"),
    # ... (start, end, text) 每句一段
]
parts = []
for s, e, t in subs:
    t_esc = t.replace("'", "\\'")
    parts.append(
        f"drawtext=enable='between(t,{s},{e})':"
        f"text='{t_esc}':x=(w-text_w)/2:y=h-120:"
        f"fontsize={FONT_SIZE}:fontcolor=white:"
        f"borderw=3:bordercolor=black@0.5:fontfile={FONT}"
    )
filter_complex = ",".join(parts)

# 合并视频+字幕+音频
ffmpeg -y -i video_no_audio.mp4 \
  -vf filter_complex -c:v libx264 -preset fast -crf 20 -map 0:v \
  -i full_narration.mp3 -c:a aac -b:a 192k -map 1:a -shortest \
  output_final.mp4
```

### 7. Discord 上传（绕过 8MB 限制）
```python
import requests
from pathlib import Path

TOKEN_FILE = Path.home() / ".discord-cli" / "token"
lines = TOKEN_FILE.read_text().strip().splitlines()
token = lines[1].strip()

# 先压缩（Discord 附件上限 8MB）
# ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 26 -c:a aac -b:a 128k output_compressed.mp4

with open("output_compressed.mp4", "rb") as f:
    files = {"file": ("video.mp4", f, "video/mp4")}
    data = {"content": "文案"}
    resp = requests.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        headers={"Authorization": f"Bot {token}"},
        data=data, files=files, timeout=120
    )
    print(resp.status_code)  # 200=成功, 413=文件太大
```

---

### 坑12：Banana 服务器到 ARK 北京节点网络不稳定
- `ark.cn-beijing.volces.com` 从 Banana 服务器连接时常超时
- **解法**：提交任务用 Python requests（timeout=30），轮询用 curl（--max-time 15），分开处理避免单次超时卡住整个流程
- 图片用 `data:image/jpeg;base64,{b64}` 内联方式提交，不依赖外部 URL

### 坑13：base64 图片 + Python requests 有长度限制
- 图片 base64 后字符数可能超过 curl ARG_MAX（系统级 Argument list too long）
- **解法**：用 Python requests 的 json 参数提交，不要用 curl + -d '{"image":"data:..."}'

## 新增踩坑（2026-04-12）

### 坑5：mmx video generate --download 参数不生效
- 症状：加了 `--download path.mp4 --no-wait` 却没生成文件
- 原因：`--no-wait` 时 mmx 立即返回 task_id，download 在异步完成后才写文件，但进程已退出
- **解法**：不用 `--download`，用 `--no-wait` 拿 task_id，再用 `mmx video task get --task-id` 查到 file_id，最后用 `mmx video download --file-id <id> --out path.mp4`

### 坑6：Hailuo 视频生成配额耗尽
- `MiniMax-Hailuo-2.3-Fast-6s-768p` 配额极少（3次/日），日常耗尽
- `MiniMax-Hailuo-2.3` 也很快超限额
- **解法1**：配额耗尽时用 `ffmpeg -stream_loop -1` 做 Ken Burns 静态图视频撑场面
- **解法2**：等待配额刷新（每日重置）
- **解法3**：用图片首帧引导生成，确保风格一致

### 坑7：Discord 附件 413 和压缩参数
- 视频 > 8MB 直接 413，用 `ffmpeg -crf 26 -c:a aac -b:a 128k` 压缩可压到 5-6MB
- 压太狠（crf 28+）画面模糊，crf 26 是画质和大小的平衡点

### 坑8：视频延伸的 setpts 必要性
- `stream_loop` 直接循环会有 PTS 累加问题，导致音视频不同步
- **必须加** `-vf "setpts=PTS-STARTPTS"` 重置时间戳

### 坑9：Remotion 项目输出路径
- Remotion Studio 项目在 Banana 服务器 `/tmp/remotion-video/`
- 最终输出 MP4 放 `/tmp/video_output/`（避免被 Remotion build 污染）
- 截图必须提前放到 `public/screenshots_v3/` 才能被 `staticFile()` 读取

### 坑10：MiniMax TTS 用 mmx 不用 curl
- mmx CLI: `mmx speech synthesize --region cn --voice "Chinese..." --text "..." --non-interactive --output out.mp3`
- 直接 curl 调 API 有签名问题，用 mmx 绕过去
- voice 推荐：`Chinese (Mandarin)_Female_Professional` 或 `Chinese (Mandarin)_Male_Announcer`

### 坑11：Remotion Ken Burns 对非16:9图片的处理
- 对于非16:9截图（如 1280×560），Remotion Ken Burns 特效无法自动裁剪
- 解法：截图尺寸要尽量用 16:9（1280×720），或者在 browser_navigate 时调整 viewport 为 16:9 比例

---

## 新增路线B：Remotion + 官网截图 + MiniMax TTS（2026-04-12 成功）

适用于：没有 Hailuo 配额、预算有限、或需要精确控制视频内容的场景。

### 流程总览
写文案 → TTS配音（MiniMax） → 测量音频时长 → 按时长规划场景 → 截官网图 → Remotion合成 → 压缩 → 发Discord

### Step 1：规划视频结构
```python
scenes = [
    {"title": "亿电通 GreenGrid", "subtitle": "跨境电力设备 B2B 贸易平台", "seconds": 3.0},
    {"title": "产品分类", "subtitle": "变压器/断路器/电缆/电表，一站式选品", "seconds": 3.0},
    {"title": "解决方案", "subtitle": "四大核心业务板块，全链路数字化管理", "seconds": 3.0},
    # ... 继续
]
total_duration = sum(s["seconds"] for s in scenes)  # 用作 TTS 目标时长参考
```

### Step 2：TTS 配音（MiniMax mmx CLI）
```bash
VOICE="Chinese (Mandarin)_Female_Professional"
TEXT="亿电通 GreenGrid，跨境电力设备 B2B 贸易平台。专注智能电网与新能源，为全球买家和卖家提供商机匹配、资信评级、询价报价、物流清关、支付收汇等全链路服务。"

mmx speech synthesize \
  --region cn \
  --voice "$VOICE" \
  --text "$TEXT" \
  --non-interactive \
  --output /tmp/greengrid_narration.mp3
```
测量：`ffprobe -i /tmp/greengrid_narration.mp3 -show_entries format=duration -of csv=p=0`

### Step 3：截官网图（browser_navigate）
```python
# 提前规划好要截的页面 URL 列表
urls = [
    "https://ec.greengrid.com.cn",
    "https://ec.greengrid.com.cn/product",
    "https://ec.greengrid.com.cn/solution",
    "https://ec.greengrid.com.cn/business",
    "https://ec.greengrid.com.cn/cooperation",
    "https://ec.greengrid.com.cn/login",
    "https://ec.greengrid.com.cn/inquiry/publish",
    "https://ec.greengrid.com.cn/dashboard",
]
# 每截一张保存为 sceneN.jpg 到 /tmp/remotion-video/public/screenshots_v3/
```

### Step 4：Remotion 配置（字幕 + Ken Burns）
```typescript
// src/Root.tsx - 字幕配置文件结构
export interface SceneConfig {
  image: string;
  title: string;
  subtitle: string;
  startTime: number;
  endTime: number;
}

const scenes: SceneConfig[] = [
  { image: "screenshots_v3/scene1.jpg", title: "亿电通 GreenGrid", subtitle: "跨境电力设备 B2B 贸易平台", startTime: 0, endTime: 3 },
  // ...
];

export { scenes };
```

Ken Burns 用 CSS `scale` + `translate` 实现（避免 ffmpeg crop 问题）：
```css
/* scene.module.css */
@keyframes kenBurns {
  0%   { transform: scale(1) translate(0, 0); }
  100% { transform: scale(1.08) translate(-1%, -0.5%); }
}
```

### Step 5：Remotion build + render
```bash
cd /tmp/remotion-video
# 截图放到 public/screenshots_v3/
cp /tmp/scene*.jpg public/screenshots_v3/

# 编辑 src/Root.tsx 填入场景数据
npm run build 2>&1 | tail -5

# 渲染（总时长 = 音频时长，帧率30）
npx remotion render out /tmp/video_output/greengrid_remotion.mp4 \
  --width 1280 --height 720 --frame-rate 30 --crf 20 \
  --duration-in-frames 720  # 24s @ 30fps
```

### Step 6：合并音频 + 烧录字幕
```python
# 字幕配置（与 TTS 节奏同步）
subs = [
    (0.0, 3.0, "亿电通 GreenGrid，跨境电力设备 B2B 贸易平台"),
    (3.0, 6.0, "专注智能电网与新能源领域，一站式全链路服务"),
    # ...
]

# ffmpeg 字幕烧录（简体中文字幕）
FONT = "/usr/share/fonts/truetype/wenquanyi/WenQuanYiZenHei.ttf"
parts = []
for s, e, t in subs:
    t_esc = t.replace("'", "\\'").replace(":", "\\:")
    parts.append(
        f"drawtext=enable='between(t,{s},{e})':"
        f"text='{t_esc}':x=(w-text_w)/2:y=h-100:"
        f"fontsize=40:fontcolor=white:"
        f"borderw=3:bordercolor=black@0.6:fontfile={FONT}"
    )
filter_complex = ",".join(parts)

ffmpeg -y -i /tmp/video_output/greengrid_remotion.mp4 \
  -vf "$filter_complex" \
  -c:v libx264 -preset fast -crf 20 -r 30 \
  -i /tmp/greengrid_narration.mp3 -c:a aac -b:a 96k -map 1:a \
  -shortest \
  /tmp/video_output/greengrid_with_audio.mp4
```

### Step 7：压缩 + Discord 上传
```bash
# 压缩（Discord 8MB 限制，crf 24 压到 ~4MB 质量很好）
ffmpeg -y -i /tmp/video_output/greengrid_with_audio.mp4 \
  -c:v libx264 -preset fast -crf 24 -maxrate 2M -bufsize 4M \
  -c:a aac -b:a 96k -movflags +faststart \
  /tmp/video_output/greengrid_final.mp4

# Discord API 直接上传（绕过 CLI bug）
python3 - << 'EOF'
import requests
token = open("/home/banana/.discord-cli/token").read().strip().splitlines()[1]
channel_id = "1492697325204672592"  # 当前子区

with open("/tmp/video_output/greengrid_final.mp4", "rb") as f:
    files = {"file": ("video.mp4", f, "video/mp4")}
    data = {"content": "视频文案"}
    r = requests.post(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        headers={"Authorization": f"Bot {token}"},
        data=data, files=files, timeout=120
    )
    print(r.status_code, r.json().get("id", r.text[:100]))
EOF
```

## 亿电通官网核心信息（视频素材参考）

- **品牌定位**：智能电网&新能源，深度价值链管理平台
- **slogan**：亿电通，让全球贸易更简单
- **核心数据**：80+市场 / 2000+海外客户 / 12+系统解决方案
- **服务链**：商机匹配 / 资信评级 / 询价跟进 / AR检验 / 在线下单 / 研发设计 / 定制金融 / 报关清关 / 物流发货 / 支付收汇 / 出口退税
- **里程碑**：2005成立 → 2012投资巴西电网 → 2014巴西办 → 2018平台转型 → 2019研发中心 → 2020 ISO认证 → 2021 GREENGRID上线
- **全球布局**：巴西/沙特/澳大利亚 常驻办
