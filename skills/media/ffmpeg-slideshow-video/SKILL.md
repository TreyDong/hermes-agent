---
name: ffmpeg-slideshow-video
description: 用 ffmpeg 把截图合成带 Ken Burns 效果、渐变叠加层、字幕的中文图片轮播视频。触发：截图轮播视频、官网介绍视频、幻灯片视频。
category: media
---

# ffmpeg 图片轮播视频生成（中文场景）

用 ffmpeg 把截图合成带 Ken Burns 效果、渐变叠加层、字幕的视频。

## 核心架构：预渲染分层 + overlay 叠加

不要在一条 ffmpeg 滤镜链里做所有事情（Ken Burns + 渐变 + 文字）。这个环境的 ffmpeg 对复杂滤镜链有兼容性问题。

**正确方案：**
1. 预渲染「图片 Ken Burns 视频」（KB视频）
2. 预渲染「文字视频」（渐变背景 + 标题 + 副标题）
3. 用 `overlay` 把两者叠加

## Ken Burns 实现（不用 zoompan）

`zoompan` 在某些 ffmpeg 版本不支持 `enable` 选项。

**替代方案：多档位预生成 + overlay 拼接**
```bash
# 预放大三张图片（1.0x / 1.06x / 1.12x）
ffmpeg -y -loop 1 -i img.png \
  -vf "scale=1280:720:force_original_aspect_ratio=increase" \
  -frames:v 1 -f image2 base.png

# overlay 拼接（3档位各 ~2.3s）
ffmpeg -y \
  -loop 1 -i base.png -loop 1 -i zoom1.png -loop 1 -i zoom2.png \
  -filter_complex "[0:v]scale=1280:720[a];[a][1:v]overlay=0:0:enable='between(t,2.3,4.6)'[b];[b][2:v]overlay=0:0:enable='gt(t,4.6)'" \
  -t 7 -r 30 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p kb.mp4
```

## 文字视频实现

**渐变背景用 `color` 源生成：**
```bash
ffmpeg -y -filter_complex "
  color=c=0x0a1628:s=1280x720:d=7:r=30[bg];
  [bg]drawbox=x=0:y=420:w=1280:h=300:color=black@0.85:t=fill[bg2];
  [bg2]drawbox=x=0:y=520:w=1280:h=200:color=black@0.60:t=fill[bg3];
  [bg3]drawtext=text='标题':fontfile=/path/to/wqy-zenhei.ttc:fontcolor=0xf0c040:fontsize=64:borderw=3:bordercolor=black@0.6:x=(w-text_w)/2:y=440[ttxt];
  [ttxt]drawtext=text='副标题':fontfile=/path/to/wqy-zenhei.ttc:fontcolor=0xc8ddf0:fontsize=24:x=(w-text_w)/2:y=520
" -t 7 -r 30 -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p txt.mp4
```

**注意：每个 filter 输出必须有 `[name]` 标签，最后一个 drawtext 可以省略输出标签。**

## 叠加合成

```bash
ffmpeg -y -i kb.mp4 -i txt.mp4 \
  -filter_complex "[0:v][1:v]overlay=0:0[out]" \
  -map "[out]" -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p out.mp4
```

## 方案B：硬切幻灯片（无动效）

用户要求「画面不要移动，要硬切切换」时，用此方案。比分层 overlay 方案更简洁。

**核心流程：**
1. 每张图生成独立视频片段（带 ASS 字幕 + fade in/out）
2. ffmpeg concat 合并为完整视频
3. 混合配音音频

### ASS 字幕（推荐）

比 drawtext 更适合多行居中字幕，支持换行、描边、渐变：

```bash
# 生成 ass 文件
cat > /tmp/sub_0.ass << 'ASSEOF'
[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Alignment, MarginL, MarginR, MarginV
Style: Default,WenQuanYi Zen Hei,56,&H00FFFFFF,&H00000000,&H00000000,-1,2,20,20,30

[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0,0:00:00.00,0:00:06.80,Default,亿电通 GreenGrid\n跨境电力设备B2B平台
ASSEOF

# 片段命令（scale→crop→ass→fade in/out）
ffmpeg -y -loop 1 -i img.jpg \
  -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,ass=/tmp/sub_0.ass,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=6.3:d=0.5:alpha=1" \
  -t 6.8 -r 30 -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p \
  seg_0.mp4
```

> ASS 中换行用 `\N`，非 `\n`。Alignment=2 是底部居中。

### 合并片段

```bash
# concat.txt 格式
echo "file '/tmp/seg_0.mp4'" > /tmp/concat.txt
echo "file '/tmp/seg_1.mp4'" >> /tmp/concat.txt
...

ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt \
  -c copy /tmp/video_no_audio.mp4

# 混合配音
ffmpeg -y -i /tmp/video_no_audio.mp4 -i /tmp/audio.mp3 \
  -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 128k -shortest \
  /tmp/final.mp4
```

**时间轴策略：先生成 TTS 获取精确时长，再分配场景数量**
```bash
# 1. 先生成配音，获取精确毫秒
SCRIPT="配音文案..."
mmx speech synthesize --voice "Chinese (Mandarin)_Mature_Woman" --text "$SCRIPT" --output /tmp/audio.mp3
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/audio.mp3)
SCENE_DUR=$(awk "BEGIN {printf \"%.2f\", $DURATION / $SCENE_COUNT}")

# 2. 每个场景 = 总时长 / 场景数
```

---

## 已知坑点

### `bc` 命令不存在
此环境无 `bc`，所有浮点运算用 `awk`：
```bash
# ❌ 错误
FRAMES=$(echo "$SCENE_DUR * 30" | bc)
# ✅ 正确
FRAMES=$(awk "BEGIN {printf \"%.0f\", $SCENE_DUR * 30}")
```

### drawbox 不认 `H` 变量
```bash
# ❌ 错误
"drawbox=x=0:y=H-80:w=1200:h=65:..."
# ✅ 正确（用像素值）
"drawbox=x=0:y=640:w=1200:h=65:..."
```

### drawbox alpha 格式
```bash
# ❌ 错误
"color=black@0.6"
# ✅ 正确
"color=black@0.6:t=fill"   # drawbox 需要 t=fill
```

### concat 对音频流的要求
如果各 segment 音轨不一致（有无音轨），concat 会失败。给每个 segment 补静音音轨：
```bash
# 每个 segment 加入 anullsrc（-f lavfi -i 要在 -i 之后）
ffmpeg -y -loop 1 -i img.png \
  -f lavfi -i anullsrc=r=44100:cl=stereo \
  -t 7 -vf "scale=..." -c:v libx264 ... \
  -c:a aac -b:a 128k -shortest seg.mp4
```

### overlay 滤镜的 label 链
每个滤镜的输出必须用 `[name]` 标记。
```bash
# ❌ 最后一行没有 [g2] 会导致 "matches no streams"
"[g1]drawbox=...:color=black@0.35:enable='lt(t,7)'"  # 没有 [g2] 输出
# ✅ 正确
"[g1]drawbox=...:color=black@0.35:enable='lt(t,7)'[g2]"
```

### Remotion 在服务器环境慎用
Remotion 需要 chromium + Node.js 依赖，版本兼容性坑多（React 17/18 冲突、chromium 不兼容）。截图轮播类视频用纯 ffmpeg 更稳定。

## 音频混音

背景音乐 -18dB（音量 0.13）：
```bash
ffmpeg -y -i nar_trimmed.aac -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.13[bg];[0:a][bg]amix=inputs=2:duration=first:normalize=0[mixed]" \
  -map "[mixed]" -c:a aac -b:a 128k -ar 44100 mixed.aac
```

## 中文支持

文泉驿字体（大多数 Linux 系统自带）：
```bash
FONT="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
```

## 触发条件

- 用户要求做「截图轮播视频」「官网介绍视频」「幻灯片视频」
- 有截图 + 配音需求
- 需要 Ken Burns 效果 + 文字叠加

## 关键经验

### Minimax TTS 文件路径
`--output` 参数有时不生效，文件实际保存在：
```
~/.hermes/hermes-agent/speech_YYYY-MM-DD-HH-MM-SS.mp3
```
需要手动 find 定位后 cp 到目标路径。

### Remotion v4 在服务器环境的问题
Remotion 需要 chromium + Node.js 依赖，版本兼容性坑多（React 17/18 冲突、chromium 不兼容、`useVideoConfig` 在根组件不可用、`Composition` 注册方式变更）。**简单幻灯片视频用纯 ffmpeg 更稳定。**
