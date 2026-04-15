---
name: netlify-manual-deploy-workflow
description: Netlify 手动部署站点的源码下载与更新流程——无 GitHub 绑定时如何拿到源码并重新部署
category: devops
---

# Netlify 手动部署站点 · 源码下载与更新

## 适用场景
- 线上站点没有绑定 GitHub（手动 deploy）
- 无法从域名直接 curl 源码（JS 渲染返回 404）
- 需要改源码但没有本地文件

## 完整流程

### 1. 列出所有站点，找到 site_id
```bash
netlify sites:list
# 输出包含每个站点的 id（GUID 格式）
```

### 2. 查询站点文件清单（确认源码结构）
```bash
netlify api listSiteFiles --data '{"site_id":"<SITE_ID>"}'
# 返回该站点已部署的所有文件 path + sha + deploy_id
```

### 3. 找到最新 deploy_id
```bash
netlify api listSiteDeploys --data '{"site_id":"<SITE_ID>"}'
# 返回 deploy 列表，找 state=ready 且 published_at 最新那个
# 记下 deploy_id 和 deploy_ssl_url（如 69d9b78c84c0f65cb112c2bf--glittering-kleicha-278c22.netlify.app）
```

### 4. 从 deploy URL 下载源码
```bash
curl -sL "https://<deploy_id>--<site-name>.netlify.app/<file-path>" -o /tmp/output.html
# 注意：是 deploy 子域名前缀，不是主域名！
```

### 5. 修改后重新部署
```bash
cd /path/to/source-dir
netlify deploy --dir=. --site=<SITE_ID> --prod --no-build
# --prod 直接发生产环境，--no-build 跳过构建（静态文件直传）
```

## 关键坑
- `netlify deploy --site=<name>` 找不到未 link 的项目，用 **site ID（GUID）** 代替
- 主域名 curl 得到 404 ≠ 没文件，可能是 SPA/SSR；必须用 `--deploy-url` 前缀下载
- `netlify sites:list` 里的 name 是子站名（如 `glittering-kleicha-278c22`），不是 GitHub repo 名
