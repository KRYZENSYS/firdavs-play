"""Missions endpoints."""
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.db.models import Mission, UserMission
from app.schemas import MissionOut
from app.services.audit import log_audit

router = APIRouter()


@router.get("", response_model=list[MissionOut])
async def list_missions(user: CurrentUser, request: Request):
    db = request.state.db
    missions = (await db.execute(select(Mission).where(Mission.is_active == True))).scalars().all()  # noqa
    user_missions = (await db.execute(
        select(UserMission).where(UserMission.user_id == user.id, UserMission.completed == False)
    )).scalars().all()
    progress_map = {um.mission_id: um for um in user_missions}
    out = []
    for m in missions:
        um = progress_map.get(m.id)
        out.append(MissionOut(
            id=m.id, code=m.code, title=m.title, description=m.description,
            type=m.type, goal=m.goal, reward_coins=m.reward_coins,
            progress=um.progress if um else 0,
            completed=um.completed if um else False,
            claimed=um.claimed if um else False,
        ))
    return out


@router.post("/{mission_id}/claim", response_model=MissionOut)
async def claim_mission(mission_id: int, user: CurrentUser, request: Request):
    db = request.state.db
    um = (await db.execute(
        select(UserMission).where(UserMission.user_id == user.id, UserMission.mission_id == mission_id)
    )).scalar_one_or_none()
    if not um or not um.completed or um.claimed:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Mission not claimable")
    mission = (await db.execute(select(Mission).where(Mission.id == mission_id))).scalar_one_or_none()
    if not mission:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mission not found")
    user.coins += mission.reward_coins
    user.xp += mission.reward_xp
    um.claimed = True
    await log_audit(db, user.id, "mission.claim", metadata={"mission_id": mission_id, "reward": mission.reward_coins})
    return MissionOut(
        id=mission.id, code=mission.code, title=mission.title, description=mission.description,
        type=mission.type, goal=mission.goal, reward_coins=mission.reward_coins,
        progress=um.progress, completed=um.completed, claimed=um.claimed,
    )
