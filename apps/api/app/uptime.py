"""
Uptime keeper: pings self every 4 minutes.
Without this, Replit puts the VM to sleep after ~5 min of no HTTP traffic.
"""
import asyncio
import logging
import os

import httpx

logger = logging.getLogger(__name__)


async def self_ping_loop(port: int):
    """Ping our own /healthz endpoint every 4 minutes to stay alive."""
    url = f"http://0.0.0.0:{port}/healthz"
    # Wait a bit before first ping (let server start)
    await asyncio.sleep(30)
    while True:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url)
                logger.debug(f"Self-ping status={r.status_code}")
        except Exception as e:
            logger.debug(f"Self-ping failed: {e}")
        await asyncio.sleep(240)  # 4 min
