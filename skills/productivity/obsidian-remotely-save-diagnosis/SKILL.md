---
name: obsidian-remotely-save-diagnosis
description: 通过 WSL2 SSH 远程诊断 Windows Obsidian Remotely Save 同步错误（401/403）
triggers:
  - Remotely Save 401
  - Obsidian 同步认证失败
  - WSL2 访问 Windows Obsidian
---

# Obsidian Remotely Save 故障诊断

## 触发条件
- Obsidian Remotely Save 同步报 401/403/认证错误
- 需要远程查看 Windows 上 Obsidian 的插件配置

## 关键路径速查

### Windows Obsidian vault 位置
```
C:\Users\<用户名>\AppData\Roaming\obsidian\obsidian.json  ← vault 列表
```
通过 WSL2 访问：`/mnt/c/Users/<用户名>/AppData/Roaming/obsidian/`

### Remotely Save 插件配置
```
<vault_path>/.obsidian/plugins/remotely-save/data.json  ← 加密配置（含 token）
<vault_path>/.obsidian/plugins/remotely-save/manifest.json  ← 版本信息
```
通过 WSL2 访问 vault：`/mnt/d/Knowledge/`（D盘）

### 快速 SSH + WSL2 诊断命令（banana 用户）
```bash
# 本案例的已知参数
WSL_USER="banana"
WSL_PASS="0112"
WSL_IP="192.168.31.81"
VAULT_ON_WINDOWS="D:\\Knowledge"   # 当前打开的 vault
VAULT_ALT="\\\\nas\\知识库\\"        # 另一 vault（指向 NAS 网络驱动器）

# 通过 WSL2 访问 vault
sshpass -p '0112' ssh -o StrictHostKeyChecking=no banana@192.168.31.81 'ls /mnt/d/Knowledge/.obsidian/plugins/'

# 列出 vault（WSL 映射路径）
# D: -> /mnt/d/  | C: -> /mnt/c/  | 网络驱动器 \\nas\ -> WSL 里可能不可直接访问
```

## 401 常见原因
1. **S3/R2**：Access Key 或 Secret Key 错误；Token 过期
2. **WebDAV**：用户名/密码错；部分服务（群晖）需要 App Password
3. **Git**：Personal Access Token 过期或缺少 `repo` 权限
4. **Vault 冲突**：两个 vault 路径指向同一文件夹，Remotely Save 检测到冲突

## 注意
- `data.json` 配置是加密的（fudge 编码），不能直接读取 token
- `obsidian.log` 通常不记录 Remotely Save 的详细错误
- 错误信息需在 Obsidian 界面弹窗或 Remotely Save 的 sync output panel 查看

## fnOS WebDAV 排查（本案例重点）

### fnOS WebDAV 端点
- 端口: **5005**（不是 5006）
- PROPFIND 可用: `curl -X PROPFIND -u "user:pass" http://127.0.0.1:5005/ --header "Depth: 1"`
- 返回 `401 Unauthorized` + `Www-Authenticate: Basic realm="Restricted"` → 认证失败
- **fnOS 用独立的用户系统，不依赖 Linux 系统账号**（WSL 的 banana:0112 不适用）

### fnOS WebDAV 找凭据
- 在 fnOS 网页后台设置的账号密码，非 WSL/Linux 账号
- WebDAV 服务路径: `/usr/trim/bin/webdav`
- systemd service: `/etc/systemd/system/webdav.service`

### 401 部分失败的常见原因
- **WebDAV 对特定文件名编码处理不一致**（中文文件名、空格、v2 后缀）
- 截图案例中失败的文件: `摘要_xxx_v2.md`、`含空格的文件名`
- 同一次同步中部分成功部分失败 → 很可能是文件名问题而非全局认证问题
