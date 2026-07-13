#!/usr/bin/env bash
# Replit startup: install deps, build web, start API (which also serves built web + bot)
set -e

echo "╔════════════════════════════════════════╗"
echo "║  🎮 FIRDAVS PLAY — Starting on Replit ║"
echo "╚════════════════════════════════════════╝"

# Frontend deps
if [ ! -d "apps/web/node_modules" ]; then
  echo "📦 Installing web dependencies..."
  cd apps/web && npm install --no-audit --no-fund --legacy-peer-deps && cd ../..
fi

# Frontend build (only if out/ missing)
if [ ! -d "apps/web/out" ]; then
  echo "🔨 Building web..."
  cd apps/web && npm run build && cd ../..
fi

# Backend deps
if [ ! -d "apps/api/venv" ]; then
  echo "🐍 Setting up Python venv..."
  cd apps/api
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  cd ../..
fi

# Copy frontend build into api/static (single port)
mkdir -p apps/api/static
cp -r apps/web/out/* apps/api/static/ 2>/dev/null || true

# Start API (serves /api/v1, Telegram bot, and frontend static)
echo "🚀 Launching unified server on port ${PORT:-3000}..."
cd apps/api
source venv/bin/activate 2>/dev/null || true
exec python main.py
