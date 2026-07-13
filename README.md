# 🎮 Firdavs Play

> Premium Telegram Web App Gaming Platform — 13 games, real-time crash, daily bonuses, referral system, admin panel.

## 🚀 Deploy on Replit (1 minute)

1. **Import this repo into Replit** (GitHub URL: `KRYZENSYS/firdavs-play`)
2. Wait for Nix environment setup (Node 20, Python 3.12, SQLite, FFmpeg)
3. Click **Run** ▶ — `start.sh` handles everything:
   - Installs web deps
   - Builds Next.js frontend
   - Installs Python deps
   - Starts unified server (API + frontend + bot on one port)
4. Open the Webview URL — done! 🎉

### Secrets (Replit Secrets tab)
| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | No | From [@BotFather](https://t.me/BotFather) |
| `WEBAPP_URL` | No | Public URL e.g. `https://your-repl.repl.co` |
| `ADMIN_TELEGRAM_IDS` | No | Comma-separated admin Telegram IDs |
| `JWT_SECRET` | No | Long random string |
| `DEV_MODE` | No | `true` allows login without Telegram initData |

> App works without `BOT_TOKEN` — only the bot is disabled.

## 🎮 Games

🚀 Crash • 💣 Mines • 🎯 Plinko • 🎲 Dice • 🪙 Coin Flip • 🎡 Lucky Wheel • 🃏 Card Pick • 🔢 Keno • 📈 Limbo • 🎴 Hi-Lo • 🗼 Towers • 💎 Jackpot (soon) • ⚔️ Wheel Duel (soon)

## 🏗 Architecture

**Single Replit process:**
- FastAPI on `$PORT`
  - `/api/v1/*` REST API
  - `/api/docs` Swagger
  - `/ws/crash` WebSocket
  - `/` Built frontend SPA
- aiogram bot (background task, polling)
- SQLite database

## 🔧 Stack

- **Frontend**: Next.js 15 (static export), React 19, Tailwind, Framer Motion
- **Backend**: FastAPI, SQLAlchemy 2, aiosqlite
- **Bot**: aiogram 3 polling
- **Auth**: JWT + Telegram WebApp initData HMAC validation
- **Fairness**: Provably fair (HMAC-SHA256) for all games

## 🔐 Security

- JWT HS256 30-day tokens
- Telegram initData signature validation
- Provably-fair game engine
- Admin audit log
- Ban system
