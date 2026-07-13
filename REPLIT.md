# 🚀 Replit Setup — 24/7 Uptime Guide

## 1. Import
- Go to https://replit.com
- Click **Create Repl → Import from GitHub**
- URL: `https://github.com/KRYZENSYS/firdavs-play`
- Language: **Bash** (Nix is auto-detected from `replit.nix`)

## 2. Secrets (lock icon, left panel)
| Secret | Required | Notes |
|--------|----------|-------|
| `BOT_TOKEN` | Yes (for bot) | From @BotFather |
| `WEBAPP_URL` | Recommended | Your Repl URL, e.g. `https://firdavs-play.USERNAME.repl.co` |
| `ADMIN_TELEGRAM_IDS` | Optional | Comma-separated admin IDs |
| `JWT_SECRET` | Optional | Long random string |
| `DEV_MODE` | Optional | `true` = allow dev login |

## 3. Run
Click **Run ▶** — that's it. The script:
1. Installs `apps/web/node_modules`
2. Builds Next.js static export
3. Creates Python venv + installs deps
4. Copies frontend into `apps/api/static/`
5. Starts `main.py` (which starts **API + bot + self-ping**)

## 4. Keep Alive — 3 layers

### Layer 1: Built-in self-ping (in-process)
`main.py` spawns a background task that pings `/healthz` every **4 minutes** internally. This keeps the Replit VM warm.

### Layer 2: External uptime monitor (recommended)
- Go to https://uptimerobot.com (free)
- Add HTTP monitor: `https://your-repl.repl.co/healthz`
- Interval: **5 minutes**
- This pings from outside, so even if internal self-ping fails, the VM stays alive

### Layer 3: Replit "Always On" (paid)
- Replit Core plan → enable Always On for guaranteed 24/7
- Without it, the VM sleeps after ~5 min of no external traffic

## 5. Bot auto-reconnect
The bot uses a **forever-retry loop** with exponential backoff:
- Polls Telegram continuously
- If disconnected (network, Telegram maintenance, etc.) — waits 1s, retries
- Backoff doubles each failure, capped at 60s
- As soon as connection returns, backoff resets
- Self-ping every 4 min also verifies bot is reachable via `get_me()`

## 6. Check health
Visit `https://your-repl.repl.co/healthz`:
```json
{
  "status": "ok",
  "service": "firdavs-play",
  "uptime_seconds": 3600,
  "bot": {"running": true, "errors": 0}
}
```

## 7. Verify bot
Send `/ping` to your bot in Telegram — it will reply `🏓 Pong!`

## Architecture

```
┌─────────────── Single Replit Process ────────────────┐
│                                                       │
│  main.py (uvicorn 0.0.0.0:$PORT)                      │
│  ├── FastAPI routes                                  │
│  │   ├── /api/v1/*                                    │
│  │   ├── /healthz                                     │
│  │   └── / (static frontend SPA)                      │
│  │                                                    │
│  └── Background tasks:                                │
│      ├── start_bot() — aiogram polling forever        │
│      │   └── self_ping_loop() — get_me every 4 min    │
│      └── self_ping_loop() — ping /healthz every 4 min │
│                                                       │
│  SQLite (firdavs.db)                                  │
│                                                       │
└───────────────────────────────────────────────────────┘
```
