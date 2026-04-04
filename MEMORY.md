# Hermes Memory

## 环境与架构
- Hermes版本：Claude Code主线，OpenClaw在 localhost:18789 跑 OpenAI兼容gateway
- Honcho已集成：Session: agent:main:discord:thread:1488353006784352287:1488353006784352287:1314519770837549071，Mode: hybrid
- 已知bug：Frozen Snapshot(#3964)、Flush Agent覆盖(#2670)、Double Flush(#3059)
- **待跟进**：Honcho PR #469（修复1536维度硬编码，embedding_client.py+models.py）— 尚未merge

## Skills 生态
- skill是按需加载，非预载常驻；内置并行子Agent最多3个
- Discord斜杠命令：/thread 可用（调 discord.py Channel.create_thread）
- Hermes语音频道：stt.model误设为"whisper-1"且provider为local，每次语音静默失败。修复：删错误配置，model: base under local provider

## API & Provider
- MiniMax极速版：API=https://api.minimaxi.com
- TTS HD✅ speech-2.8-hd；图像✅ image-01；视频✅ minimax-hailuo-2.3；音乐❌ music-2.5
- VL原图>80KB会超时，压至35KB即可

## 飞书
- 应用ID: cli_a9449e4ce33a1bdb，云文档需手动在开放平台控制台添加 drive:drive + space:document:delete scope
- lark-cli keychain 锁住时用 `security unlock-keychain ~/Library/Keychains/login.keychain-db` 解锁
- cron早报 delivery: "discord:1489271050050076722"（Home 频道）

## NAS (飞牛OS fnOS)
- IP=192.168.31.154，用户=banana，密码=11114444
- SSH: `sshpass -p '11114444' ssh banana@192.168.31.154`
- 有Playwright+chromium、docker、npx；无X server需用 headless；Chrome 调试端口 9222

## jackwener CLI 三件套
- rdt-cli(Reddit)、twitter-cli(X)、xiaohongshu-cli(小红书)，github.com/jackwener；三者共用 Chrome cookie
- **xhs-cli 缺出去水印+图片二创**：客户运营流程需此能力，xhs-cli 不支持

## 跨Session参考
- sessions.json是唯一准确的 session→thread 映射来源，session文件名是 message_id 不是 thread_id
- session_search 可搜索历史 session，但无法直接查看完整内容
- cron 任务可通过 honcho_conclude 追溯 honcho session 记录
- Hermes文档直连：https://raw.githubusercontent.com/NousResearch/claude-code/main/website/docs/...
