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

