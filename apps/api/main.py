"""
Firdavs Play — unified entry point for Replit.
- FastAPI HTTP server on $PORT
- Serves /api/v1/* (auth, users, games, missions, achievements, leaderboard, admin)
- Serves built frontend from /static
- Telegram bot runs in background via aiogram polling (with auto-reconnect)
- Self-ping keeps Replit VM alive
"""
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import api_router
from app.bot import get_bot_state
from app.uptime import self_ping_loop

STATIC_DIR = Path(__file__).parent / "static"
STARTED_AT = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    await init_db()
    print("✅ Database ready")

    # Start Telegram bot in background (with auto-reconnect)
    bot_task = None
    if settings.BOT_TOKEN:
        from app.bot import start_bot
        bot_task = asyncio.create_task(start_bot(), name="telegram-bot")
        print("🤖 Telegram bot started (auto-reconnect enabled)")
    else:
        print("⚠️  BOT_TOKEN not set — running without Telegram bot")

    # Start self-ping to keep Replit alive
    port = int(os.environ.get("PORT", 3000))
    uptime_task = asyncio.create_task(self_ping_loop(port), name="self-ping")
    print("💓 Self-ping started (keeps server alive)")

    yield

    # Shutdown
    print("👋 Shutting down...")
    for task in (bot_task, uptime_task):
        if task:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass


app = FastAPI(
    title="Firdavs Play API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api/v1")


# Health check (for UptimeRobot, Replit always-on, etc.)
@app.get("/healthz")
async def healthz():
    bot = get_bot_state()
    return {
        "status": "ok",
        "service": "firdavs-play",
        "uptime_seconds": int(time.time() - STARTED_AT),
        "bot": {
            "running": bot.get("running", False),
            "errors": bot.get("errors", 0),
        },
    }


# Serve frontend static files (SPA fallback to index.html)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{path:path}")
    async def spa(path: str):
        if path.startswith("api/") or path == "healthz":
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        f = STATIC_DIR / path
        if f.is_file():
            return FileResponse(f)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root_no_build():
        return {
            "service": "Firdavs Play API",
            "status": "frontend not built",
            "docs": "/api/docs",
            "hint": "run 'npm run build' in apps/web then restart",
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
