Discord服务器香蕉 ID: 1453031874082373687
§
Hermes文档直连：https://raw.githubusercontent.com/NousResearch/hermes-agent/main/website/docs/... 用curl+grep。
§
MiniMax极速版：API=https://api.minimaxi.com；TTS HD✅图像✅视频✅音乐❌；MCP仅web_search+understand_image。
§
Hermes语音频道：stt.model设为"whisper-1"但provider是local导致静默失败。修复：model: base under local provider。
§
Hermes cron：01:00 Memory Dreaming；03:00 Skill Health Check；07:30 早报（twitter-cli）；22:00 复盘提醒；23:00 AI日记。输出: ~/.hermes/cron/output/
早报Twitter bug：Agent总把昨天推文误判为今日已发。对比createdAtLocal前8位与`date +%Y-%m-%d`。用户名=treydtw。
§
每日AI日记（23:00）：prompt使用session_search查今日对话；输出路径 `/vol1/1000/知识库/90-Daily/{date}_diary.md`
§
opencli + Mac 浏览器：搞不定的网站操作直接用 opencli operate，Mac Chrome 有真实登录态。
§
知识库路径：/vol1/1000/知识库/
目录结构：00-Inbox/01-Tasks/02-Projects/03-Output/04-Sources/05-Wiki/07-Archive/90-Daily/99-System/
05-Wiki子目录：concepts/entities/qa/summaries/comparisons/index.md/log.md/SCHEMA.md
项目库路径：/vol2/1000/项目库/（所有项目基于此目录）
§
Polanyi命名框架：讨论AI/知识/方法论时，优先用"名字调用"而非"描述"。
§
飞书项目管理Base: https://my.feishu.cn/base/EK1nb34O6a2LKbsDsmMcr4HMn5M，表ID: tbl3Ga47JV9sNzyd，字段：项目名称/描述/状态(进行中)/优先级/开始日期/截止日期/完成度/负责人。仪表盘: blk4ZO62Stb6dcLQ。
§
微信公众号已装Skill：baoyu-post-to-wechat + md2wechat。
§
dbskill知识库（2026-04-05安装）：`~/.hermes/knowledge/dbskill/`含atoms.jsonl（4176条）+10个方法论文档（action/benchmark/content/deconstruct/diagnosis等）。
§
任务目录：/vol1/1000/知识库/01-Tasks/（TaskNotes格式，markdown文件）
§
视频生成：Doubao-Seedance-2.0-260128首选。输出 /vol1/1000/知识库/20-Studio/视频生成/[Project_Name]/。
§
查GitHub用`gh`命令行，浏览器仅在需要页面交互/截图时才用。
§
Discord统一CLI：~/bin/discord-cli（Python单文件，替代原discordctl+discocli）。thread/guild/channel/msg/sync/search/serve全集命令。Token路径：~/.discord-cli/token（格式bot\nTOKEN）。

Discord Forum频道：API type=15；Forum thread：type=11。
Cron job deliver注意事项：Prompt只生成内容不要包含thread ID，让deliver机制统一路由，否则两条路径冲突。
§
工具搜索优先级：CLI → Skill → MCP内置 → find-skill → 浏览器。Browser是最末选项。Skill已创建：tool-search-priority。
§
亿电通 GreenGrid（ec.greengrid.com.cn）：跨境电力设备贸易平台，聚焦智能电网&新能源，主营商机匹配/资信评级/询价/物流/报关/支付收汇/研发设计/定制金融。目标学员：制造厂商、海外采购商。核心痛点：供应商报价比价效率低、小单多sales报价轮次多、客户询盘响应慢、样品申请流程繁琐。适合用本地OpenClaw做报价解析、BOM配置向导、快速报价生成、客服知识库自动化。
§
项目库（vol2）：/vol2/1000/项目库/，子目录无状态分类，仅`已归档/`作为归档目录。新项目直接放根目录，归档才进已归档。
§
Obsidian项目入口：/vol1/1000/知识库/02-Projects/<项目名>.md（仅一个md文件，内容为`[[file:///vol2/1000/项目库/<项目名>/README.md]]`），作为Obsidian内的入口引用，不存实际项目文件。
§
task-sync skill：任务路径`/vol1/1000/知识库/01-Tasks/`；`projectPath`字段指向`/vol2/1000/项目库/<项目名>/`；支持创建任务/创建项目（含自动建目录+Obsidian入口+关联任务）/归档项目/完成任务/取消任务/查看列表。触发检测支持自然语言意图，不止固定句式。
§
ppt-craft skill迭代记录：
- v1: 固定1280×720px viewport（bug：小框框）+ flex-start堆顶
- v2: 修复：100vw×100vh + justify-content:center
- v3: 设计升级（Notion/Mintlify风格）+ 字号提升至1.8vw body + space-between布局 + fadeUp动画 + 装饰性大号数字

谢老师项目路径：/vol2/1000/项目库/20260402-谢老师项目/html-slides-v2/output/
用户要求：字号至少36pt equivalent（1920px宽下≈1.8vw）；内容要均匀分布，不要堆叠

错误日志已写入 rule-book.md (err-001/err-002) + generator-rules.md硬规则区块
§
Banana 服务器可用的生图工具：Seedream（doubao-seedream-5-0）通过 ARK_API_KEY 工作，OpenAI/MiniMax/DashScope 均无 key。命令：npx -y bun ~/.hermes/skills/baoyu-imagine/scripts/main.ts --provider seedream --ar 16:9 --quality 2k --prompt "..." --image out.jpg
§
谢老师项目（html-slides-v2）：/vol2/1000/项目库/20260402-谢老师项目/html-slides-v2/output/；Netlify site: de65e013-2788-4314-bf75-a30b989cef1c，URL: https://html-slides-v2.netlify.app。
§
解读推特文章流程：必须优先用 x-tweet-fetcher（`fetch_tweet.py`）获取内容；搜索才用 `camofox_search`。浏览器是最后手段，且需用子agent启动。禁止直接用 browser 工具抓推文。
§
浏览器操作（网页截图/交互/填写表单等）：一律通过 delegate_task 委托给子agent执行，禁止直接在主会话中调用 browser_* 系列工具。
§
Remotion 项目路径：/tmp/video_output/remotion-video/；音频必须放 public/audio/ 才能被 staticFile() 读取；截图放 public/screenshots_v3/。Ken Burns 用 CSS width/height % 而非 ffmpeg crop（crop 对非16:9图片会失败）。字幕淡入淡出用 interpolate(absolute_time, [start-0.5, start, end, end+0.5], [0,1,1,0])。
§
多 Agent 架构区分（重要修正）：
- 垂直型（Vertical）：多个专业 Agent 平等并行工作，无中央调度者，各 Agent 各司其职通过共享上下文协作。像小组分工，没有"父 agent"的概念。
- 总管型（Hub-and-Spoke）：一个中央 Agent 统一接收任务、分配给子 Agent、汇总结果输出。像主管分配工作，有明确的总-子关系。
给企业培训讲多 Agent 时这是核心知识点，不能混为一谈。
§
Mac IP: 待补充（用户多次提醒仍记不住，需主动确认）