Discord服务器香蕉的服务器 ID: 1453031874082373687
§
Hermes文档直连路径：GitHub raw content（不依赖 docs.nousresearch.com 域名解析）—— website/docs/ 目录下的 markdown 文件可通过 https://raw.githubusercontent.com/NousResearch/hermes-agent/main/website/docs/... 访问。curl + grep 是最稳的抓取方式。Advanced路线三文档：user-guide/docker.md（Deployment）、reference/cli-commands.md（Command Reference）、developer-guide/architecture.md（Architecture）。
§
MiniMax极速版（2026-04-01实测）：API=https://api.minimaxi.com；TTS HD✅ speech-2.8-hd；图像✅ image-01；视频✅ minimax-hailuo-2.3；音乐❌ music-2.5；MCP仅web_search+understand_image，VL原图压至35KB。
§
Hermes语音频道：stt.model设为"whisper-1"（OpenAI API名）但provider是local（faster-whisper），导致每次语音静默失败。修复：删错误配置，model: base under local provider。
§
Hermes在Discord是纯文本模式，无法监听/回应语音频道。用户曾在语音里呼叫我但我没有回应。
§
Hermes cron：每日01:00 Memory Dreaming；03:00 Skill Health Check；07:30 早报（twitter-cli，Discord格式化）。输出: ~/.hermes/cron/output/
早报Twitter bug：Agent总把昨天推文误判为今日已发。对比createdAtLocal前8位与`date +%Y-%m-%d`。用户名=treydtw。
§
opencli + Mac 浏览器是最终方案：无头浏览器搞不定的网站操作，直接在 Mac 上通过 opencli operate 做。Mac Chrome 有真实登录态，配合 Browser Bridge 扩展，可以操控任何需要登录的网站。
§
qmd 知识库：/vol1/1000/知识库/（collection: docs, qmd://docs/）；旧文档库已废弃，qmd索引需重建
§
Polanyi命名框架法则（2026-04-07）：当用户讨论AI/知识/方法论时，优先用"名字调用"而非"描述"。这是指：面对一个洞见或问题，优先识别它属于哪个已有的概念框架（名字），用框架名来组织和表达，而不是自己重新描述。具体操作：1) prompt设计时引用已有框架名而非冗长描述；2) 用户积累个人知识时用概念名字归类而非逐条记录；3) 多agent通信用"任务类型+框架名"作为高效协议。核心理念：我们知道的比能表达的更多，名字是保存知识完整性最完整的形式。
§
飞书项目管理Base: https://my.feishu.cn/base/EK1nb34O6a2LKbsDsmMcr4HMn5M (token: EK1nb34O6a2LKbsDsmMcr4HMn5M)，表「项目」ID: tbl3Ga47JV9sNzyd，字段：项目名称/描述/状态(进行中)/优先级(高/中/低)/开始日期/截止日期/完成度/负责人。仪表盘ID: blk4ZO62Stb6dcLQ。
用户偏好：减少任务时直接设置提醒时间，不询问，根据任务内容判断。
§
微信公众号相关已装 Skill（2026-04-07）：baoyu-post-to-wechat（发布文章/贴图）+ md2wechat（Markdown转排版+封面生成+AI风格写作）。另有 wenyan-cli（文言CLI）可通过 npm 安装使用。
§
Discord Forum 任务频道（task）：ID=1490189325646696508
Forum 标签映射（状态）：
  规划中: 1490190116835037305
  进行中: 1490190119905263899
  已完成: 1490190125685014569
  暂停: 1490190127753072691
Forum 标签映射（优先级）：
  高优先级: 1490190186066350221
  中优先级: 1490190188847169546
  低优先级: 1490190190805782559
飞书任务→Discord Forum 联动流程：建任务时在论坛发帖子（打状态+优先级标签），状态变更时更新标签，完成时关闭帖子。
§
视频生成：Doubao-Seedance-2.0-260128（首选） + 火山方舟Seedance备选（轮询+签名下载加Host header）。输出目录 /vol1/1000/知识库/20-Studio/视频生成/[Project_Name]/，每个项目含视频+prompt.txt。偏好高质量多镜头cinematic action。视频项目跟踪用飞书Base（字段：项目名/Prompt/视频链接/创建时间）。
§
查GitHub优先用`gh`命令行，浏览器仅在需要页面交互/截图时才用。用户不喜欢我开浏览器做GitHub操作。