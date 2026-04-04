#!/bin/bash
# OpenCLI Mac Remote - Quick Commands
# Usage: bash ~/.hermes/skills/opencli-mac-remote/references/quick-commands.sh <command>

MAC_USER="xiaojigongzuoshi"
MAC_PASS="0112"
MAC_HOST="macbook-air.tailda5466.ts.net"
export PATH="/opt/homebrew/bin:$PATH"

cmd="$1"
shift

case "$cmd" in
  doctor)
    sshpass -p "$MAC_PASS" ssh -o StrictHostKeyChecking=no "$MAC_USER@$MAC_HOST" 'export PATH="/opt/homebrew/bin:$PATH"; opencli doctor'
    ;;
  state)
    sshpass -p "$MAC_PASS" ssh -o StrictHostKeyChecking=no "$MAC_USER@$MAC_HOST" 'export PATH="/opt/homebrew/bin:$PATH"; opencli operate state'
    ;;
  bilibili-hot)
    sshpass -p "$MAC_PASS" ssh -o StrictHostKeyChecking=no "$MAC_USER@$MAC_HOST" "export PATH=\"/opt/homebrew/bin:\$PATH\"; opencli bilibili hot --limit ${1:-5}"
    ;;
  xhs-search)
    sshpass -p "$MAC_PASS" ssh -o StrictHostKeyChecking=no "$MAC_USER@$MAC_HOST" "export PATH=\"/opt/homebrew/bin:\$PATH\"; opencli xiaohongshu search \"$1\""
    ;;
  twitter-timeline)
    sshpass -p "$MAC_PASS" ssh -o StrictHostKeyChecking=no "$MAC_USER@$MAC_HOST" "export PATH=\"/opt/homebrew/bin:\$PATH\"; opencli twitter timeline --limit ${1:-5}"
    ;;
  *)
    echo "Usage: $0 {doctor|state|bilibili-hot|xhs-search|twitter-timeline}"
    ;;
esac
