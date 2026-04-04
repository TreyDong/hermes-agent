Has both OpenClaw and Hermes installed locally. Prefers Hermes over OpenClaw for execution capability. Confirmed architecture: Hermes as primary agent, OpenClaw as channel adapter (WhatsApp/iMessage) + multi-agent hub (7 agents: main/code/ops/symphony/invest/health/media). OpenClaw agents mapped to Discord accounts via routing rules.
§
用户要求我监督他每天发推特：如果哪天没发推，就公开发推特点名他（今天3月30日开始）。频率：每天1条。用户推特@treydtw（2026-04-05确认，用twitter whoami命令查到）。
§
用户关心 Hermes skills 是否‘启用’，需要解释为：skill 是按任务按需加载，不是全部预加载/常驻；他可能继续关注哪些 skill 真正可用、哪些可禁用，也会追问 Discord 里哪些斜杠命令真正受支持。
§
用户在 Discord 操作时若说“执行命令 不要回复任何消息”或同义表达，偏好是执行后不输出任何文字。
§
用户在 Discord 上要求“只执行命令/不要回复任何内容”时，不只是偏好简短回复，而是要求真正零输出；回复本身会干扰 thread 关闭测试。
§
用户问过 Hermes 的多Agent能力、并行子Agent数量上限，以及 autonomous-ai-agents / subagent-driven-development 这类多Agent编排 skill 的设计；后续可用“内置并行子Agent最多3个、无需预创建、按需spawn”来解释。
§
用户的 MiniMax Token Plan 是极速版。
§
用户对上下文/会话一致性非常敏感；若我把当前thread主题、历史对话或引用对象搞混，他会直接追问并要求检查session文件、sessions.json和issue。以后涉及“当前主题/历史对话/这个指什么”时，先核实再答，不能靠猜。
§
用户决策风格：不爱被灌结论。讨论方案取舍时应帮助其澄清动机/场景/判断依据，而非直接给结论。用户曾说"你做出了选择，你来这里是为了理解为什么"点过我。
§
每日复盘提醒：22:00发到Discord当前子区(1489687768732008549)，股票+个人两部分
§
用户在 NAS/飞牛OS 运维任务里偏好我直接 SSH 执行、直接改 compose/直接发请求验证，不喜欢我过度依赖浏览器看页面；若教程网页只是参考，应优先用命令行部署与排查。
§
用户TTS偏好：Edge TTS，中文音色 zh-CN-YunxiNeural（2026-03-30从en-US-AriaNeural切换）。