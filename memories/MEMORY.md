CLI: /Users/Treydong/bin/discord-ops。用户说“子区”即 Discord thread。若只 archive 线程，thread 会移到线程列表，但父频道主聊天区里的入口消息可能仍可见；若要彻底隐藏入口，需要删除 thread starter message（父频道里的发起消息，ID 通常等于 thread_id）再 archive。用户说“只执行/不要回复任何消息”时，执行完不输出任何文字。
§
Hermes文档直连路径：GitHub raw content（不依赖 docs.nousresearch.com 域名解析）—— website/docs/ 目录下的 markdown 文件可通过 https://raw.githubusercontent.com/NousResearch/hermes-agent/main/website/docs/... 访问。curl + grep 是最稳的抓取方式。Advanced路线三文档：user-guide/docker.md（Deployment）、reference/cli-commands.md（Command Reference）、developer-guide/architecture.md（Architecture）。
§
MiniMax极速版（2026-04-01实测）：API=https://api.minimaxi.com；TTS HD✅ speech-2.8-hd；图像✅ image-01；视频✅ minimax-hailuo-2.3；音乐❌ music-2.5；MCP仅web_search+understand_image，VL原图压至35KB。
§
飞书CLI（2026-04-04更新）：v1.0.3，安装在NAS（/home/banana/.lark-cli/），不在Mac。重新OAuth授权后所有scope均已包含（calendar/mail/im/drive删除等）。auth login会缓存token在Keychain，修改权限后必须重新auth login才能使新scope生效。
§
Hermes语音频道：stt.model设为"whisper-1"（OpenAI API名）但provider是local（faster-whisper），导致每次语音静默失败。修复：删错误配置，model: base under local provider。
§
Hermes在Discord是纯文本模式，无法监听/回应语音频道。用户曾在语音里呼叫我但我没有回应。
§
Hermes Discord session加载Bug（2026-04-06）：gateway/session.py 的 load_transcript() 只读 .jsonl，但 run_agent.py 写 session 用的是 sessions/session_{id}.json（三源：jsonl/json/SQLite取最长）。修复已写但需restart gateway生效。sessions.json索引有时脱节（指向旧session ID）。
§
我运行在 NAS（192.168.31.154）本地，不是远程连接。直接执行命令，无需 sshpass/ssh。
NAS 用户：banana（sudo 免密），Docker 数据目录：/vol1/docker。
飞书CLI（/home/banana/.lark-cli/）、千帆（/home/banana/.cf/）都在本地。
Mac 上只有 opencli + Chrome 浏览器供远程操控网页用。
§
Hermes cron：每日01:00 Memory Dreaming；03:00 Skill Health Check；07:30 早报（twitter-cli，Discord格式化）。输出: ~/.hermes/cron/output/
早报Twitter bug：Agent总把昨天推文误判为今日已发。对比createdAtLocal前8位与`date +%Y-%m-%d`。用户名=treydtw。
§
Skills精简至118个（2026-04-06）：删gaming/smart-home/godmode/audiocraft/tensorrt-llm/pytorch-fsdp/nemo-curator/polymarket/blogwatcher/domain-intel/duckduckgo-search/minimax-direct-api/inference-sh-cli；保留remotion/whisper/dogfood/opencli-operate及lark-*/github*/mlops推理类。
§
火山方舟Seedance（2026-04-06实测）：subagent轮询异步任务稳定，完整URL写文件再读防截断，签名下载需加Host header。Skill: volcengine-seedance-video（media/）。
§
opencli + Mac 浏览器是最终方案：无头浏览器搞不定的网站操作，直接在 Mac 上通过 opencli operate 做。Mac Chrome 有真实登录态，配合 Browser Bridge 扩展，可以操控任何需要登录的网站。
§
用户视频/媒体文件存放目录：/vol1/1000/文档库/20-Studio/（飞牛OS路径）
§
qmd 知识库路径：/vol1/1000/文档库/（collection: docs, qmd://docs/）