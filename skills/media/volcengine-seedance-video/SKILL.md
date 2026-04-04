---
name: volcengine-seedance-video
description: 火山方舟 Seedance 全系列视频生成 API — 文生视频、图生视频（首帧/首尾帧/参考图）、多模态参考、轮询下载
triggers:
  - 火山方舟视频生成
  - Seedance API
  - ark.cn-beijing.volces.com 视频任务
  - 豆包视频生成
  - doubao-seedance
---

# volcengine-seedance-video

火山方舟 Seedance 全系列视频生成 API 调用，支持所有模型和生成模式。

## 常用模型速查

| 模型 | 模型 ID | 支持场景 | resolution 默认 | duration 范围 |
|------|---------|---------|----------------|--------------|
| **Seedance 2.0** | `doubao-seedance-2-0-260128` | 文生/图生/多模态参考/首尾帧 | 720p | 4~15s 或 -1 |
| **Seedance 2.0 fast** | `doubao-seedance-2-0-fast-260128` | 同上 | 720p | 4~15s 或 -1 |
| **Seedance 1.5 pro** | `doubao-seedance-1-5-pro-251215` | 文生/图生/首尾帧 | 720p | 4~12s 或 -1 |
| **Seedance 1.0 pro** | `doubao-seedance-1-0-pro-250220` | 文生/图生/首尾帧 | 1080p | 2~12s |
| **Seedance 1.0 pro fast** | `doubao-seedance-1-0-pro-fast-250220` | 文生/图生首帧 | 1080p | 2~12s |
| **Seedance 1.0 lite t2v** | `doubao-seedance-1-0-lite-t2v-250220` | 文生视频 | 720p | 2~12s |
| **Seedance 1.0 lite i2v** | `doubao-seedance-1-0-lite-i25-250220` | 参考图(1-4张)/首尾帧/首帧 | 720p | 2~12s |

> Seedance 2.0 系列不支持 1080p；1.0 pro/pro-fast 默认 1080p；1.0 lite 参考图场景 ratio 默认 16:9。

## API 基础信息

**Base URL：** `https://ark.cn-beijing.volces.com`
**鉴权：** `Authorization: Bearer {API_KEY}`
**创建任务：** `POST /api/v3/contents/generations/tasks`
**查询任务：** `GET /api/v3/contents/generations/tasks/{task_id}`
**任务有效期：** 7 天（超期自动清除）

---

## 场景一：文生视频（Text-to-Video）

最简场景，只需文本提示词。

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-2-0-260128",
    "content": [
      {"type": "text", "text": "小猫对着镜头打哈欠"}
    ],
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "generate_audio": true,
    "watermark": false
  }'
```

---

## 场景二：图生视频·首帧（Image-to-Video / First Frame）

输入 1 张图片作为视频首帧，模型生成后续画面。
**role：** `first_frame` 或留空（两者等价）。

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-2-0-260128",
    "content": [
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/first_frame.jpg"},
        "role": "first_frame"
      },
      {"type": "text", "text": "一只橘猫从窗台跳下"}
    ],
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "generate_audio": true,
    "watermark": false
  }'
```

**输入要求：**
- 格式：jpeg、png、webp、bmp、tiff、gif（2.0 还支持 heic/heif）
- 宽高比（宽/高）：(0.4, 2.5)
- 宽高长度：300~6000 px
- 单张大小：< 30 MB

---

## 场景三：图生视频·首尾帧（First + Last Frame）

输入首帧和尾帧图片，模型生成中间过渡。
**role：** 首帧=`first_frame`，尾帧=`last_frame`。

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-2-0-260128",
    "content": [
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/first.jpg"},
        "role": "first_frame"
      },
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/last.jpg"},
        "role": "last_frame"
      },
      {"type": "text", "text": "苹果从枝头落到桌上"}
    ],
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "generate_audio": true,
    "watermark": false
  }'
```

> 首尾帧图片宽高比不一致时，以首帧为主，尾帧自动裁剪适配。
> `return_last_frame: true` 可获取生成视频的尾帧图像（用于接续生成）。

---

## 场景四：多模态参考（Reference Images + Videos + Audio）

仅 **Seedance 2.0 / 2.0 fast** 支持。可同时输入：
- 参考图：0~9 张（role: `reference_image`）
- 参考视频：0~3 个（role: `reference_video`）
- 参考音频：0~3 段（role: `reference_audio`）
- 文本提示词（可选，但建议填写）

**注意：** 不可单独输入音频，至少需要 1 个参考视频或图片。

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-2-0-260128",
    "content": [
      {
        "type": "text",
        "text": "全程使用视频1的第一视角构图，全程使用音频1作为背景音乐..."
      },
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/pic1.jpg"},
        "role": "reference_image"
      },
      {
        "type": "image_url",
        "image_url": {"url": "https://example.com/pic2.jpg"},
        "role": "reference_image"
      },
      {
        "type": "video_url",
        "video_url": {"url": "https://example.com/ref_video1.mp4"},
        "role": "reference_video"
      },
      {
        "type": "audio_url",
        "audio_url": {"url": "https://example.com/bgm.mp3"},
        "role": "reference_audio"
      }
    ],
    "generate_audio": true,
    "ratio": "16:9",
    "duration": 11,
    "watermark": false
  }'
```

**参考图输入要求：**
- 数量：1~9 张
- 同图片通用要求

**参考视频输入要求：**
- 格式：mp4、mov
- 分辨率：480p、720p
- 时长：单个 2~15s，总时长 ≤15s
- 总像素数：640×640 ~ 834×1112（即 409600~927408）
- 单个文件：≤50 MB

**参考音频输入要求：**
- 格式：wav、mp3
- 时长：单个 2~15s，总时长 ≤15s
- 单个文件：≤15 MB

---

## 场景五：联网搜索（tools）

Seedance 2.0 / 2.0 fast 支持联网搜索，模型可根据提示词自主搜索互联网内容（商品、天气等），提升视频时效性。

```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-2-0-260128",
    "content": [
      {"type": "text", "text": "今日北京天气如何？"}
    ],
    "tools": [{"type": "web_search"}],
    "ratio": "16:9",
    "duration": 5,
    "watermark": false
  }'
```

---

## 场景六：样片模式（Draft）

仅 **Seedance 1.5 pro** 支持。先用 `draft: true` 生成预览视频（480p，成本低），确认满意后再用 `draft_task.id` 生成正式视频。

**Step 1：生成 Draft**
```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [{"type": "text", "text": "小猫打哈欠"}],
    "draft": true
  }'
```

**Step 2：基于 Draft ID 生成正式视频**
```bash
curl -s -X POST "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {API_KEY}" \
  -d '{
    "model": "doubao-seedance-1-5-pro-251215",
    "content": [
      {
        "type": "draft_task",
        "draft_task": {"id": "cgt-draft-xxx"}
      }
    ],
    "draft": false,
    "resolution": "720p"
  }'
```

> Draft 视频仅保存 7 天；Draft 模式不支持返回尾帧、不支持离线推理。

---

## 常用可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `resolution` | string | 因模型而异 | `480p` / `720p` / `1080p`（2.0系列不支持） |
| `ratio` | string | `adaptive`（2.0默认） | `16:9` / `4:3` / `1:1` / `3:4` / `9:16` / `21:9` / `adaptive` |
| `duration` | int | 5 | 秒；2.0/1.5: 4~12（或-1智能）；1.0: 2~12 |
| `seed` | int | -1（随机） | [-1, 2^32-1]，相同seed相似结果 |
| `watermark` | bool | false | 是否带水印 |
| `camera_fixed` | bool | false | 固定摄像头（1.0系列支持，2.0不支持） |
| `generate_audio` | bool | true | 是否生成同步音频（2.0/1.5支持） |
| `return_last_frame` | bool | false | 返回生成视频的尾帧图像（PNG） |
| `service_tier` | string | `default` | `default`（在线）/ `flex`（离线，2.0不支持）|
| `execution_expires_after` | int | 172800 | 任务超时秒数，取值 [3600, 259200] |
| `callback_url` | string | - | 任务状态变化时回调此 URL |

---

## 轮询任务状态

```bash
curl -s -X GET "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{TASK_ID}" \
  -H "Authorization: Bearer {API_KEY}"
```

状态值：`queued` → `running` → `succeeded` / `failed` / `expired`

轮询策略：每 30 秒一次，最多 200 次（约 100 分钟），超时标记 `expired`。

---

## 下载视频（Python）

API 返回的视频 URL 签名参数在终端显示可能被截断（实际完整），用 Python 下载最可靠：

```python
import urllib.request, json

url = "..."  # 从任务响应 content.video_url 获取
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as resp, open("output.mp4", "wb") as out:
    while chunk := resp.read(65536):
        out.write(chunk)
```

> 不带 `User-Agent` header 会返回 403。

---

## 查询用量

管控面用量 API 需要控制台登录态，API Key 无法直接调用。
请到控制台：**费用中心 → 用量查询 → 火山方舟**，按模型名过滤。

---

## 常见问题

**Q: URL 显示截断（`...`），下载 403？**
A: 终端显示截断是视觉问题，URL 实际完整（Credential 79字符、Signature 64字符均正常）。下载必须带 `User-Agent: Mozilla/5.0` header，否则 403。

**Q: 音频参考和 generate_audio 同时用？**
A: 可以。`reference_audio` 控制背景音乐，`generate_audio: true` 生成人声/音效，两者独立工作。

**Q: 任务一直 running 最久多久？**
A: 默认 48 小时（`execution_expires_after`: 172800s），实际通常 2-5 分钟。

**Q: Seedance 2.0 支持 1080p 吗？**
A: 不支持。2.0 系列最高 720p；1.0 pro/pro-fast 默认 1080p。

**Q: 图片/视频/音频有真人脸被拦截？**
A: 2.0 系列对含真人人脸的参考图/视频有限制，平台有专项解决方案，详见文档"教程"页面。2026-03-11 起，本账号产出的 2.0 视频作为输入素材不再触发此限制。

**Q: `duration: -1` 是什么意思？**
A: 由模型在有效范围内自主选择整数秒时长。实际时长会反映在查询响应的 `duration` 字段中。

**Q: 如何实现连续视频（尾帧接续）？**
A: 创建任务时加 `"return_last_frame": true`，查询任务获取尾帧 PNG，再以该图片作为下一个任务的首帧输入。
