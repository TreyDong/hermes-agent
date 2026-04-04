#!/bin/bash
# Kill existing Chrome
pkill -f "Google Chrome" 2>/dev/null
sleep 2
# Start Chrome with remote debugging
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome" \
  --no-first-run \
  --no-default-browser-check \
  2>/dev/null &
sleep 5
echo "Chrome started with debug port on 9222"
