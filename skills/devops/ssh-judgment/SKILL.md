---
name: ssh-judgment
description: SSH判断规则 — 执行前先查hostname，避免不必要的SSH跳转
---
# SSH Judgment Rule

## Trigger
Any task involving SSH or remote machine operations.

## Rule
**Before SSHing, check `hostname` first.**

| hostname | Location | Action |
|----------|----------|--------|
| `nas` / `Nas` | Already on NAS | Execute locally, do NOT SSH |
| other | On another machine | SSH to target if needed |

## Why This Matters
MEMORY may record NAS IP (192.168.31.154), but that doesn't mean every operation requires SSH. If hostname=nas, the current shell is already on NAS. SSH is only for operating a *different* machine.

## Example of the Bug This Prevents
- ❌ Wrong: See "NAS" in context → immediately `ssh 192.168.31.154` 
- ✅ Right: Check `hostname` → if "nas", run commands directly in current shell
