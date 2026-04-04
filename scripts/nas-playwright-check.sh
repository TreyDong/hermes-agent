#!/bin/bash
sshpass -p '11114444' ssh banana@192.168.31.154 << 'EOF'
echo "=== Playwright check ==="
npx playwright --version 2>&1 | head -2
echo "=== chromium path ==="
ls ~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome 2>/dev/null
echo "=== camoufox check ==="
ls ~/.cache/camoufox/browser/chrome 2>/dev/null
echo "=== node version ==="
node --version
echo "=== openviking workspace ==="
ls ~/openviking-deploy/ 2>/dev/null | head -10
EOF
