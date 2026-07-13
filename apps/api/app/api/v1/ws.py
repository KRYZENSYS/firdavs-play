"""WebSocket endpoints: real-time crash rounds, chat, leaderboard updates."""
import asyncio
import json
import random
from datetime import datetime
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.services.websocket_manager import ws_manager
from app.services.games.crash import crash_point, payout_multiplier

router = APIRouter()


@router.websocket("/crash")
async def crash_socket(ws: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001)
        return
    user_id = int(payload.get("sub", 0))

    await ws_manager.connect(ws, "crash", user_id)
    try:
        while True:
            await asyncio.sleep(8)
            rnd = random.random()
            crash = crash_point(rnd)
            mult = payout_multiplier(crash)
            await ws_manager.broadcast("crash", {
                "type": "crash_round",
                "crash_point": crash,
                "payout_max": mult,
                "started_at": datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(ws, "crash", user_id)
    except Exception:
        ws_manager.disconnect(ws, "crash", user_id)


@router.websocket("/chat")
async def chat_socket(ws: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001)
        return
    user_id = int(payload.get("sub", 0))
    await ws_manager.connect(ws, "chat", user_id)
    try:
        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue
            content = str(msg.get("content", "")).strip()[:500]
            if not content:
                continue
            await ws_manager.broadcast("chat", {
                "type": "chat",
                "user_id": user_id,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(ws, "chat", user_id)


@router.websocket("/notifications")
async def notifications_socket(ws: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload:
        await ws.close(code=4001)
        return
    user_id = int(payload.get("sub", 0))
    await ws_manager.connect(ws, f"user:{user_id}", user_id)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws, f"user:{user_id}", user_id)
