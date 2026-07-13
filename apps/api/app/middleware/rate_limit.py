"""Per-IP rate limiting middleware backed by Redis."""
from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.services.redis_service import redis_service

log = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 60, period: int = 60) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self._skip_paths = {"/health", "/", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self._skip_paths or path.startswith("/ws/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        key = f"rl:{client_ip}:{path}"
        try:
            allowed, remaining = await redis_service.rate_limit_check(key, self.calls, self.period)
        except Exception as e:
            log.warning("rate_limit.redis_error", error=str(e))
            return await call_next(request)

        if not allowed:
            log.warning("rate_limit.exceeded", ip=client_ip, path=path)
            return ORJSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "retry_after": self.period},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
