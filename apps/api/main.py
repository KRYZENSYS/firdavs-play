"""
Firdavs Play — unified entry point for Replit.
- FastAPI HTTP server on $PORT
- Serves /api/v1/* (auth, users, games, missions, achievements, leaderboard, admin)
- Serves built frontend from /static (single port — no separate web server needed)
- Telegram bot runs in background via aiogram polling
"""
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import api_router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    await init_db()
    print("✅ Database ready")

    # Start Telegram bot in background (only if token provided)
    bot_task = None
    if settings.BOT_TOKEN:
        from app.bot import start_bot
        bot_task = asyncio.create_task(start_bot())
        print("🤖 Telegram bot started")
    else:
        print("⚠️  BOT_TOKEN not set — running without Telegram bot")

    yield

    # Shutdown
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    print("👋 Shutdown complete")


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


# Health check (for Replit)
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "firdavs-play"}


# Serve frontend static files (SPA fallback to index.html)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/")
    async def root():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{path:path}")
    async def spa(path: str):
        # Don't shadow API routes
        if path.startswith("api/") or path == "healthz":
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        # Serve real file if it exists
        f = STATIC_DIR / path
        if f.is_file():
            return FileResponse(f)
        # SPA fallback
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
    # 0.0.0.0 is required for Replit
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
