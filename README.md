# 🎮 Firdavs Play

> Premium Telegram Web App Gaming Platform — 13 ta o'yin, real-time multiplayer, provably fair, anti-cheat, va to'liq admin panel.

![Status](https://img.shields.io/badge/status-MVP_Phase_1-00d9ff?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-a855f7?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-Next.js_+_FastAPI_+_PostgreSQL_+_Redis-22c55e?style=for-the-badge)

## ✨ Features

### 🎮 13 ta O'yin
- **Crash** · **Mines** · **Plinko** · **Dice** · **Coin Flip** · **Lucky Wheel** · **Card Pick**
- **Keno** · **Limbo** · **Hi-Lo** · **Towers** · **Jackpot** · **Wheel Duel** (PvP)

### 👤 Profil va Daraja
- Telegram Login, avatar, username
- Level + XP tizimi
- Badge va Achievementlar
- Kunlik/Haftalik bonuslar
- Daily/Weekly missions
- Inventar, statistika, o'yin tarixi

### 🏆 Ijtimoiy
- Global leaderboard
- Referral tizimi
- Do'stlar ro'yxati
- Global chat
- Clan/Guild
- Turnirlar
- Sovg'a yuborish
- Profilni ulashish

### 🎁 Mukofotlar
- Promo kodlar
- Daily spin
- Mystery Box
- Seasonal Pass
- Eventlar
- Achievement mukofotlari

### 🛡 Admin Panel
- Foydalanuvchilar, statistikalar
- O'yin sozlamalari, event yaratish
- Banner, promo, xabar yuborish
- Audit loglar, anti-cheat nazorati

### 🔒 Xavfsizlik
- Rate limiting, anti-cheat
- Server-side game validation
- Audit logs, secure API
- JWT auth, provably fair RNG

## 🛠 Texnologiyalar

**Frontend:** Next.js 15 · TypeScript · Tailwind · Framer Motion · Lottie · Telegram SDK
**Backend:** FastAPI · Python 3.12 · PostgreSQL 16 · Redis 7 · WebSocket · SQLAlchemy 2 · Alembic
**Bot:** aiogram 3 · APScheduler
**Infra:** Docker · Nginx · Grafana · Prometheus · Sentry

## 🚀 Quick Start

```bash
git clone https://github.com/KRYZENSYS/firdavs-play.git
cd firdavs-play
cp .env.example .env
docker compose up -d
```

## 📁 Project Structure

```
firdavs-play/
├── apps/
│   ├── web/          # Next.js 15 — Telegram Web App UI
│   ├── api/          # FastAPI — Game engine + REST + WebSocket
│   └── bot/          # aiogram 3 — Telegram bot
├── packages/
│   └── shared/       # Shared types, schemas, utilities
├── docker/
│   ├── nginx/        # Reverse proxy + SSL
│   └── postgres/     # Init scripts
├── docker-compose.yml
└── .env.example
```

## 🎨 Design

Premium dark gaming UI — neon ko'k-binafsha, glassmorphism, smooth animatsiyalar, Lottie effektlar, ovoz + haptic feedback, ko'p tilli (UZ/RU/EN).

## 📜 License

MIT © KRYZENSYS
