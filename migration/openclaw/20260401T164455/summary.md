# OpenClaw -> Hermes Migration Report

- Timestamp: 20260401T164455
- Mode: execute
- Source: `/home/banana/.openclaw`
- Target: `/home/banana/.hermes`

## Summary

- migrated: 9
- archived: 12
- skipped: 23
- conflict: 0
- error: 0

## What Was Not Fully Brought Over

- `/home/banana/.openclaw/workspace/AGENTS.md` -> `(n/a)`: No workspace target was provided
- `(n/a)` -> `/home/banana/.hermes/memories/MEMORY.md`: Source file not found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/.env`: No allowlisted Hermes-compatible secrets found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/.env`: No Slack settings found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/.env`: No WhatsApp settings found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/.env`: No Signal settings found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/.env`: No provider API keys found
- `/home/banana/.openclaw/openclaw.json` -> `/home/banana/.hermes/config.yaml`: No TTS configuration found in OpenClaw config
- `(n/a)` -> `/home/banana/.hermes/skills/openclaw-imports`: No OpenClaw skills directory found
- `(n/a)` -> `/home/banana/.hermes/skills/openclaw-imports`: No shared OpenClaw skills directories found
- `(n/a)` -> `/home/banana/.hermes/tts`: Source directory not found
- `/home/banana/.openclaw/openclaw.json` -> `(n/a)`: Selected Hermes-compatible values were extracted; raw OpenClaw config was not copied.
- `/home/banana/.openclaw/memory/main.sqlite` -> `(n/a)`: Contains secrets, binary state, or product-specific runtime data
- `/home/banana/.openclaw/credentials` -> `(n/a)`: Contains secrets, binary state, or product-specific runtime data
- `/home/banana/.openclaw/devices` -> `(n/a)`: Contains secrets, binary state, or product-specific runtime data
- `/home/banana/.openclaw/identity` -> `(n/a)`: Contains secrets, binary state, or product-specific runtime data
- `(n/a)` -> `(n/a)`: No MCP servers found in OpenClaw config
- `(n/a)` -> `(n/a)`: No cron configuration found
- `(n/a)` -> `(n/a)`: No browser configuration found
- `(n/a)` -> `(n/a)`: No approvals configuration found
- `(n/a)` -> `(n/a)`: No memory backend configuration found
- `(n/a)` -> `(n/a)`: No UI/identity configuration found
- `(n/a)` -> `(n/a)`: No logging/diagnostics configuration found
