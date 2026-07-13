from fastapi import APIRouter

from app.api.v1 import auth, users, games, missions, leaderboard, admin, promo, ws, notifications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(promo.router, prefix="/promo", tags=["promo"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])
