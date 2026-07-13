"""Redis client wrapper for caching, rate-limiting, and pub/sub."""
import redis.asyncio as aioredis
import structlog

from app.core.config import settings

log = structlog.get_logger()


class RedisService:
    _client: aioredis.Redis | None = None

    async def connect(self) -> None:
        if self._client is not None:
            return
        self._client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        await self._client.ping()
        log.info("redis.connected", url=settings.REDIS_URL)

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None
            log.info("redis.disconnected")

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return self._client

    # --- Cache helpers ---
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        await self.client.set(key, value, ex=ex)

    async def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return await self.client.delete(*keys)

    async def incr(self, key: str, amount: int = 1) -> int:
        return await self.client.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> None:
        await self.client.expire(key, seconds)

    # --- Rate limit ---
    async def rate_limit_check(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        """Returns (allowed, remaining). Increments counter and sets TTL on first hit."""
        cur = await self.client.incr(key)
        if cur == 1:
            await self.client.expire(key, window)
        ttl = await self.client.ttl(key)
        return (cur <= limit, max(0, limit - cur))

    # --- Atomic ops ---
    async def get_json(self, key: str) -> dict | None:
        import json
        raw = await self.client.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value: dict, ex: int | None = None) -> None:
        import json
        await self.client.set(key, json.dumps(value, default=str), ex=ex)


redis_service = RedisService()
