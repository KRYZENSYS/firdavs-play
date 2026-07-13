# 🎮 Firdavs Play — Ultra Premium Telegram WebApp Gaming Platform

> Premium Telegram-based gaming platform with 13 casino-style games, real-time WebSocket gameplay, and a full social/loyalty system.

![Status](https://img.shields.io/badge/status-ready-success)
![Stack](https://img.shields.io/badge/stack-Next.js%20%2B%20FastAPI%20%2B%20aiogram%203-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### 🎮 13 Games (Provably Fair)
- **Crash** — Live multiplier, cashout anytime
- **Mines** — Reveal safe tiles, avoid mines
- **Plinko** — Drop ball, win up to x1000
- **Dice** — Roll over/under, custom target
- **Coin Flip** — Heads or tails, x1.95
- **Lucky Wheel** — Spin & win up to x10
- **Card Pick** — Pick the highest card
- **Keno** — Pick numbers, draw 10
- **Limbo** — Custom multiplier target
- **Hi-Lo** — Higher or lower card
- **Towers** — Climb & avoid bombs
- **Jackpot** — Coming soon
- **Wheel Duel** — Coming soon

### 👥 Social & Gamification
- 🏆 **Leaderboards** (Coins, XP, Wagered)
- 🎯 **Daily & Weekly Missions**
- 🏅 **Achievements** (auto-unlock)
- 👥 **Friend system** with gifts
- 💬 **Real-time chat** (WebSocket)
- 📲 **Live crash rounds** (WebSocket)
- 🔔 **Push notifications**

### 💎 Economy
- 💰 Coins, XP, Level system
- 🎁 Daily bonus (100 coins) + Weekly (1000)
- 🎟 Promo codes
- 👥 Referral program (500 coins each)
- 🏪 Inventory & items

### 🛡 Admin Panel
- 📊 Real-time stats dashboard
- 👤 User management (ban, coin adjust)
- 🎟 Promo code creation
- 📜 Full audit logs
- 📢 Broadcast notifications

## 🏗 Architecture

```
firdavs-play/
├── apps/
│   ├── api/          # FastAPI backend (Python 3.12)
│   ├── bot/          # Telegram bot (aiogram 3)
│   └── web/          # Next.js 15 frontend
├── deploy/           # Nginx, SSL configs
└── docker-compose.yml
```

### Stack
- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Zustand, Socket.io
- **Backend**: FastAPI, SQLAlchemy 2 (async), asyncpg, Redis, Alembic
- **Bot**: aiogram 3, APScheduler
- **DB**: PostgreSQL 16, Redis 7
- **Deploy**: Docker, Nginx, Let's Encrypt

## 🚀 Quick Start

### Prerequisites
- Docker 24+ & Docker Compose 2+
- Telegram bot token (from @BotFather)
- Domain pointing to your server

### 1. Clone & Configure

```bash
git clone https://github.com/KRYZENSYS/firdavs-play.git
cd firdavs-play
cp .env.example .env
# Edit .env with your values
```

### 2. Set Up Bot

Talk to @BotFather, run `/newapp` for your bot, get a bot token.

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_BOT_USERNAME=FirdavsPlayBot
```

### 3. Launch

```bash
docker compose up -d
docker compose logs -f api
```

The first run applies migrations and seeds default missions, achievements, and promo codes.

### 4. Set Up WebApp in BotFather

1. `/mybots` → Select your bot → Bot Settings → Menu Button
2. Set URL to `https://firdavs-play.com`
3. Or use `/setdomain` for direct Web App URL

## 📚 API Docs

Once running:
- **Swagger**: https://api.firdavs-play.com/docs
- **ReDoc**: https://api.firdavs-play.com/redoc
- **OpenAPI**: https://api.firdavs-play.com/openapi.json

## 🎨 Design System

- **Colors**: Deep dark (#0a0e1a) + Cyan accent (#00d9ff) + Purple glow (#a855f7)
- **Glassmorphism**: backdrop-blur + rgba backgrounds
- **Animations**: Framer Motion + Three.js + GSAP
- **Mobile-first**: 100% responsive, gesture-friendly

## 🔐 Security

- JWT auth with rotating secrets
- Telegram initData HMAC-SHA256 validation
- Per-IP rate limiting (60 req/min)
- Per-user rate limiting (30 bets/min)
- Daily wager caps
- Anti-cheat win-rate monitor
- SQL injection-proof (parameterized queries)
- XSS/CSRF protection
- Security headers (CSP, HSTS, X-Frame-Options)

## 📊 Performance

- Redis caching for leaderboards
- WebSocket connection pooling
- Database connection pooling (asyncpg)
- Async I/O throughout
- Static asset CDN-ready
- Multi-worker uvicorn

## 🧪 Default Promo Codes

- `WELCOME100` — 100 coins (10k uses)
- `FIRDAVS2026` — 1000 coins (1k uses)
- `PREMIUM500` — 500 coins (500 uses)

## 📄 License

MIT — see [LICENSE](LICENSE)

## 👤 Author

**Firdavs** — [@FirdavsVIP](https://t.me/FirdavsVIP)
