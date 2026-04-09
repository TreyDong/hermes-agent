# Memory
§
问题很清楚了。在 `auth.py` 第 43 行：

```python
jar = loader(domain_name=".xiaohongshu.com")
```

`.xiaohongshu.com` 这个前缀过滤太严格了——Chrome 实际存储的部分 cookie domain 不是以点开头的，或者恰恰相反是更具体的子域名，导致匹配不上。

修复：去掉点，改用 `"xiaohongshu.com"` 作为 substring 匹配，同时增加 `"chengfeng.xiaohongshu.com"` 兜底。

§
[main 793023f] fix(auth): 扩大 cookie domain pattern 匹配范围，提升登录成功率
 1 file changed, 31 insertions(+), 20 deletions(-)

§
[Banana] 修复https://github.com/TreyDong/chengfeng-cli 这个项目里面获取cookies的部分，匹配的ip太少，导致用户进入首页的时候会获取不到cookies

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

