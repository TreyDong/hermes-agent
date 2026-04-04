Discord服务器香蕉的服务器 ID: 1453031874082373687
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
我的 HERMES_HOME=/home/banana/.hermes/（NAS），配置文件都在 NAS 上，不是 Mac 上。SOUL.md 存在于 /home/banana/.hermes/SOUL.md。
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
§
Polanyi命名框架法则（2026-04-07）：当用户讨论AI/知识/方法论时，优先用"名字调用"而非"描述"。这是指：面对一个洞见或问题，优先识别它属于哪个已有的概念框架（名字），用框架名来组织和表达，而不是自己重新描述。具体操作：1) prompt设计时引用已有框架名而非冗长描述；2) 用户积累个人知识时用概念名字归类而非逐条记录；3) 多agent通信用"任务类型+框架名"作为高效协议。核心理念：我们知道的比能表达的更多，名字是保存知识完整性最完整的形式。
§
飞书项目管理Base: https://my.feishu.cn/base/EK1nb34O6a2LKbsDsmMcr4HMn5M (token: EK1nb34O6a2LKbsDsmMcr4HMn5M)，表「项目」ID: tblXk8QjpHEhVeZQ，字段：ID/项目名称/描述/状态/优先级/开始日期/截止日期/负责人/完成度。后续用 lark-base skill 操作。
用户偏好：减少任务时直接设置提醒时间，不询问，根据任务内容判断。
§
User prefers video generation outputs to be organized in a specific directory structure: `/vol1/1000/文档库/20-Studio/视频生成/[Project_Name]/`. Each project folder should contain the video file and a `prompt.txt` file.
§
User wants a multi-dimensional table (e.g., Feishu Base) to track video generation projects, including fields for Project Name, Prompt, Video Link/File, and Creation Time.
§
User is using Doubao-Seedance-2.0-260128 for video generation and prefers high-quality, multi-segment cinematic action sequences (e.g., 'Jian Lai' style).