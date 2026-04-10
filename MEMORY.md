# Memory
§
Notion AI CLI（April 8）：`/home/banana/bin/notion-ai-cli`——opencli经LAN IP(192.168.31.132)操控Mac Chrome，JS注入触发Notion AI回复；需探索Notion API替代GUI方案

§
Discord bot token失效（April 9）：cron 22:00复盘提醒发送失败，discocli返回401；token MTQ4ODc3OT...已过期，需重新获取并更新到discocli token文件和openclaw.json

§
Honcho NAS部署（April 9）：FN OS原生服务占用8000/5432/6379/9090端口；调整compose映射到8100/5433/6380/9091；官方v3.0.5模板有CACHE_URL指向database而非redis的bug

§
x-tweet-fetcher bug修复：HTTPError是URLError子类，异常处理顺序错误导致404被归类为"网络错误"；已修复异常处理顺序

§
Skills生态：~150+ skills，覆盖飞书/Discord/MLOps/社交媒体；skills目录`~/.hermes/skills/`

§
核心CLI工具：lark-cli（飞书）、discord-discocli（Discord）、opencli-operate（Mac浏览器自动化）

§
task-sync skill：Discord帖子↔飞书任务↔本地文档三方同步，真相源`/vol1/1000/知识库/00-HQ/TASK.md`；已知bug修复：subtasks create的CLI语法用--params而非--task-guid flag

§
知识库路径：`/vol1/1000/知识库/`，含00-HQ/、60-Wiki/、dbskill/等子目录

§
活跃项目：Hermes教程（橙皮书风格，任务已建）；Auto Research pipeline（选题→自动研究→素材库→人工加工→发布）；Notion AI操作（opencli经LAN IP连接Mac Chrome）

§
Twitter @treydtw；Honcho Memory系统；DREAMS.md记录梦境/cron输出

§
Discord已知问题：/model切换命令在Discord通道不生效（April 8调查过）

§
Banana项目：用现有memory系统重构task-sync的memory部分，不单独新建memory（April 8讨论）

