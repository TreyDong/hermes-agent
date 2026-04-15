Hermes为主力agent（`~/.hermes/`），OpenClaw作渠道适配（WhatsApp/iMessage）。并行子Agent最多3个、按需spawn，无需预创建。
§
用户要求监督每天发推特（@treydtw）。如哪天没发就公开发推特点名。频率：每天1条。
§
用户对上下文/会话一致性非常敏感；若把当前thread主题、历史对话搞混，他会直接追问并要求检查session文件、sessions.json和issue。以后涉及"当前主题/历史对话/这个指什么"时，先核实再答，不能靠猜。
§
用户决策风格：不爱被灌结论。讨论方案取舍时应帮助其澄清动机/场景/判断依据，而非直接给结论。
§
honcho memory provider init持续失败（No such file or directory）；`honcho_profile`返回空、`honcho_search`有输出。
§
每日复盘提醒：22:00发到Discord当前子区(1489687768732008549)，股票+个人两部分
§
用户在NAS/飞牛OS运维任务里偏好直接SSH执行、直接改compose/直接发请求验证，不喜欢过度依赖浏览器；若教程网页只是参考，应优先用命令行部署与排查。
§
Discord操作：若说"执行命令/只执行/不要回复任何消息"→真正零输出。视频生成后直接发文件到当前子区，不只发文字。文件路径 /tmp/video_output/。
§
英文技术名词后面加中文注解或英文翻译，避免纯英文术语无解释