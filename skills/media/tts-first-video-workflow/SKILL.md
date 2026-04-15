---
name: tts-first-video-workflow
description: 旁白优先的 AI 视频制作工作流 — 先 TTS 配音，按音频时长生成视频，再合成。解决配音和视频不同步、字幕时机错乱的问题。
triggers:
  - 旁白优先 视频
  - TTS 视频 同步
  - 中文配音 视频生成
  - mmx 视频旁白
  - 广告视频 制作流程
---

# TTS 优先视频制作工作流

## 核心原则

传统做法（错）：
1. 生成视频
2. 再配旁白
3. 结果：视频和配音时长对不上，衔接生硬

正确做法：
1. **写旁白文案**
2. **生成 TTS 配音** → 获得精确时长
3. **按时长切分视频段** → 每段 = 对应音频片段时长
4. **AI 生成每段视频** → 用首帧图引导风格
5. **合并 + 烧录字幕** → 按音频时间轴逐句显示
6. **合成音视频**

---

## 完整流程

### 1. 写旁白文案（按段落分）
```bash
mkdir -p /tmp/video_project/sections
mkdir -p /tmp/video_project/assets
```

旁白格式：
```
【第一段 · 开场 0-8秒】
亿电通，让全球电力设备贸易更简单。
我们专注智能电网与新能源领域...

【第二段 · 平台价值 8-20秒】
从供应商报价比价，到采购询盘响应...
```

### 2. TTS 生成（MiniMax mmx CLI）
```bash
VOICE="Chinese (Mandarin)_Male_Announcer"  # 男声播音员

# 每段单独生成，方便控制
mmx speech synthesize --region cn --voice "$VOICE" \
  --text "第一段文字..." \
  --non-interactive --output sections/s1.mp3

mmx speech synthesize --region cn --voice "$VOICE" \
  --text "第二段文字..." \
  --non-interactive --output sections/s2.mp3
```

### 3. 合并音频 + 测量时长
```bash
cat > sections/list.txt << 'EOF'
file 's1.mp3'
file 's2.mp3'
file 's3.mp3'
file 's4.mp3'
EOF

ffmpeg -y -f concat -safe 0 -i sections/list.txt -c copy sections/full_narration.mp3

# 测量每段和总时长
python3 -c "
import subprocess, json
sections = {'s1': 'sections/s1.mp3', 's2': 'sections/s2.mp3', ...}
for name, path in sections.items():
    r = subprocess.run(['ffprobe','-v','quiet','-print_format','json','-show_format',path],
                      capture_output=True, text=True)
    d = json.loads(r.stdout)
    dur = float(d['format']['duration'])
    print(f'{name}: {dur:.1f}s')
"
```

### 4. AI 生成每段视频
```bash
# 每段视频目标时长 = 对应音频片段时长
# 注意：Hailuo 实际产出约 5.9 秒（10秒模型实际产约6秒），需后续延伸

mmx video generate \
  --model MiniMax-Hailuo-2.3 \
  --first-frame "assets/scene1.jpg" \
  --prompt "英文视频描述..." \
  --no-wait --quiet
# 保存 task_id
```

### 5. 下载 + 延伸视频到目标时长
```bash
# 下载
mmx video download --file-id <FILE_ID> --out sections/s1_raw.mp4 --quiet

# 延伸（Hailuo 实际短于目标时）
ffmpeg -y -stream_loop -1 -i sections/s1_raw.mp4 -t 13.3 \
  -vf "setpts=PTS-STARTPTS" \
  -c:v libx264 -preset fast -crf 23 -r 30 -an \
  sections/s1_extended.mp4
```

### 6. 合并视频
```bash
cat > sections/concat.txt << 'EOF'
file 's1_extended.mp4'
file 's2_extended.mp4'
file 's3_extended.mp4'
file 's4_extended.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i sections/concat.txt \
  -c:v libx264 -preset fast -crf 20 -r 30 \
  assets/video_no_audio.mp4
```

### 7. 烧录中文字幕
```python
import subprocess

FONT = "/usr/share/fonts/truetype/wenquanyi/WenQuanYiZenHei.ttf"
FONT_SIZE = 56

# 每句字幕: (开始秒, 结束秒, 文字)
subs = [
    (0.0, 3.0, "亿电通，让全球电力设备贸易更简单"),
    (3.0, 6.0, "我们专注智能电网与新能源领域"),
    # ...
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

cmd = [
    "ffmpeg", "-y",
    "-i", "assets/video_no_audio.mp4",
    "-vf", filter_complex,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-map", "0:v",
    "assets/video_with_subs.mp4"
]
subprocess.run(cmd)
```

### 8. 合并音视频
```bash
ffmpeg -y \
  -i assets/video_with_subs.mp4 \
  -i assets/full_narration.mp3 \
  -c:v copy -c:a aac -b:a 192k \
  -map 0:v -map 1:a -shortest \
  output_final.mp4
```

---

## 关键经验

### 音频时长 vs 视频时长
- AI 视频生成模型（Hailuo/Doubao）产出的实际时长**通常短于你设定的目标**
- Hailuo 设定 10s → 实际约 5.9s
- **必须**用 `ffmpeg -stream_loop -1 ... -t <目标时长>` 预先延伸

### 字幕字体
- Linux 服务器中文字体：`/usr/share/fonts/truetype/wenquanyi/WenQuanYiZenHei.ttf`
- 字幕大小：56pt（1920px 宽基准下约 2.9vw，1080p 视频约 38pt）
- 字幕位置：底部 y=h-120，水平居中

### Discord 视频上传
- Discord 附件上限 **8MB**
- 最终视频需要压缩：`ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 26 -c:a aac -b:a 128k output_compressed.mp4`
- crf 26 可压到 5-6MB，画质可接受

### mmx CLI 配额注意
- `mmx quota show` 查剩余次数
- Hailuo-2.3-Fast-6s 配额极少（3次/日），日常主要用普通 2.3
- 配额耗尽时：用 Ken Burns 静态图视频代替、AI 图延伸
