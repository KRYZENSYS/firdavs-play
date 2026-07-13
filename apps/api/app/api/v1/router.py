"""API v1 router aggregating all endpoints."""
from fastapi import APIRouter

from app.api.v1 import auth, users, games, missions, achievements, inventory, promo, notifications, friends, leaderboard, admin, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(promo.router, prefix="/promo", tags=["promo"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
