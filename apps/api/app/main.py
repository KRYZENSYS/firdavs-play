"""Firdavs Play — FastAPI entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import structlog

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.v1.router import api_router
from app.db.session import init_db, close_db
from app.services.redis_service import redis_service
from app.services.websocket_manager import ws_manager
from app.services.scheduler import scheduler
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware

configure_logging(settings.LOG_LEVEL)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", env=settings.APP_ENV, app=settings.APP_NAME)
    await init_db()
    await redis_service.connect()
    await ws_manager.start()
    scheduler.start()
    yield
    log.info("shutdown")
    scheduler.shutdown()
    await ws_manager.stop()
    await redis_service.disconnect()
    await close_db()


app = FastAPI(
    title="Firdavs Play API",
    version="0.1.0",
    description="🎮 Premium Telegram Web App Gaming Platform",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url=None,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=settings.RATE_LIMIT_PER_MIN, period=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "firdavs-play-api", "version": "0.1.0"}


@app.get("/")
async def root():
    return {"service": "Firdavs Play API", "docs": "/docs", "version": "0.1.0"}
