---
name: minimax-tokenplan-tts
description: Use MiniMax Token Plan API key for TTS, video, image generation via mmx CLI. When user asks to generate speech/audio with a Token Plan key (sk-cp-...), use this instead of direct API calls.
---

# MiniMax Token Plan — mmx CLI 使用指南

## 识别 Token Plan Key

格式：`sk-cp-...` — 这种 key 不能直接调 API，必须用 mmx CLI。

## 安装与配置

```bash
npm install -g mmx-cli
mmx auth login --api-key "sk-cp-你的key" --region cn  # 中国用户
mmx auth login --api-key "sk-cp-你的key" --region global  # 全球用户
```

## TTS 配音生成

```bash
# 查看可用音色
mmx speech voices --region cn --output json --quiet

# 生成配音
mmx speech synthesize --region cn \
  --voice "Chinese (Mandarin)_Male_Announcer" \
  --text "要配音的文字" \
  --non-interactive
```

常用音色：
- `Chinese (Mandarin)_Male_Announcer` — 男声播音员
- `Chinese (Mandarin)_News_Anchor` — 新闻主播
- `male-qn-qingse` — 青年男声
- `female-shaonv` — 少女

## 多段 MP3 合并

```bash
# 方法1: concat协议（最简单）
ffmpeg -y -i "concat:scene1.mp3|scene2.mp3|scene3.mp3" -acodec copy combined.mp3

# 方法2: 文件列表法
ls *.mp3 | while read f; do echo "file '$f'"; done > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy combined.mp3
```

## 音视频合成

```bash
# 若音频略长于视频，调速fit
SPEED=$(python3 -c "print(26.7/25)")
ffmpeg -y -i audio.mp3 -filter:a "atempo=$SPEED" audio_adj.mp3

# 合并
ffmpeg -y -i video.mp4 -i audio_adj.mp3 \
  -c:v copy -c:a aac -map 0:v -map 1:a -shortest output.mp4
```

## 关键踩坑

1. **直接 API 调用会失败**：Token Plan key 调 `api.minimax.io` 或 `api.minimaxi.com` 会返回 2061 "token plan not support model"，但这不是真的——只是端点不对
2. **正确的端点**：`mmx` CLI 内部用 `api.minimax.chat`，这是 Token Plan 专用端点
3. **模型名映射**：直接 API 的 `speech-02-hd` = mmx CLI 的 `speech-2.8-hd`
4. **key 格式区别**：`sk-cp-` = Token Plan，`ey...` = 普通 API
