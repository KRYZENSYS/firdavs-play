"""WebSocket connection manager for real-time game updates."""
from collections import defaultdict
from typing import Any

from fastapi import WebSocket
import structlog

log = structlog.get_logger()


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._user_index: dict[int, set[WebSocket]] = defaultdict(set)

    async def start(self) -> None:
        log.info("ws.manager.started")

    async def stop(self) -> None:
        for channel in list(self._connections.keys()):
            for ws in list(self._connections[channel]):
                try:
                    await ws.close()
                except Exception:
                    pass
        self._connections.clear()
        self._user_index.clear()
        log.info("ws.manager.stopped")

    async def connect(self, ws: WebSocket, channel: str, user_id: int | None = None) -> None:
        await ws.accept()
        self._connections[channel].add(ws)
        if user_id is not None:
            self._user_index[user_id].add(ws)
        log.debug("ws.connect", channel=channel, user_id=user_id)

    def disconnect(self, ws: WebSocket, channel: str, user_id: int | None = None) -> None:
        self._connections[channel].discard(ws)
        if user_id is not None and user_id in self._user_index:
            self._user_index[user_id].discard(ws)
            if not self._user_index[user_id]:
                del self._user_index[user_id]
        log.debug("ws.disconnect", channel=channel, user_id=user_id)

    async def broadcast(self, channel: str, payload: Any) -> None:
        dead: list[WebSocket] = []
        for ws in self._connections.get(channel, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections[channel].discard(ws)

    async def send_to_user(self, user_id: int, payload: Any) -> None:
        dead: list[WebSocket] = []
        for ws in self._user_index.get(user_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._user_index[user_id].discard(ws)

    def channel_count(self, channel: str) -> int:
        return len(self._connections.get(channel, set()))

    def total_connections(self) -> int:
        return sum(len(s) for s in self._connections.values())


ws_manager = WebSocketManager()
