---
name: minimax-token-plan-workflow
description: MiniMax Token Plan key (sk-cp-) TTS 配音工作流 — 必须用 mmx CLI，不能直接调 API
category: media
---

# MiniMax Token Plan TTS 配音工作流

## 背景
MiniMax Token Plan 的 key（`sk-cp-` 开头）是 MCP 工具专用的，不能直接调 API。必须用 `mmx` CLI。

## 环境准备
```bash
# 1. 装 mmx CLI（只需一次）
npm install -g mmx-cli

# 2. 认证 Token Plan key
mmx auth login --api-key "sk-cp-xxx" --region cn
```

## 视频配音流程
```bash
# 3. 合成 TTS（mp3格式）
mmx speech synthesize \
  --region cn \
  --voice "speech_turian_mascot" \
  --text "这是要配音的文字内容" \
  --output /tmp/video_output/scene_01.mp3

# 4. 检查可用音色
mmx speech voices --region cn
# 常用：月暖男声(speech_turian_mascot)/知性女声(speech_turian_female)/元气少女(speech_turian_young_female)

# 5. 合并音视频
ffmpeg -i /tmp/video_output/video.mp4 -i /tmp/video_output/scene_01.mp3 \
  -map 0:v -map 1:a -shortest /tmp/video_output/final_with_audio.mp4
```

## 踩坑记录
- `speech-01-hd`、`speech-02-turbo` 在 Token Plan 套餐里返回 2061（无权限），只有 `speech-2.8-hd`（即 `speech_turian_*` 系列）可用
- API Host 是 `https://api.minimax.chat`，不是 `api.minimax.io` 或 `api.minimaxi.com`
- Token Plan key 不能用于直接 HTTP API 调用，必须走 mmx CLI

## 视频输出路径
`/tmp/video_output/`
