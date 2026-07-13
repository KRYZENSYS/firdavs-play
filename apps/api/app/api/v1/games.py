"""Game endpoints: place bet, crash cashout."""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import insert, select

from app.api.deps import CurrentUser
from app.core.config import settings
from app.db.models import GameRound
from app.schemas import BetRequest, BetResult
from app.services.audit import log_audit
from app.services.games import engine
from app.services.xp import add_xp
from app.services.anti_cheat import validate_bet

router = APIRouter()


@router.post("/bet", response_model=BetResult)
async def place_bet(body: BetRequest, user: CurrentUser, request: Request):
    db = request.state.db

    if user.coins < body.bet_amount:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient balance")
    if body.bet_amount < settings.MIN_BET or body.bet_amount > settings.MAX_BET:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Bet must be {settings.MIN_BET}-{settings.MAX_BET}")

    await validate_bet(db, user, body)

    server_seed = engine.new_server_seed()
    client_seed = body.client_seed or "default"
    nonce = user.games_played + 1

    try:
        result = engine.place_bet(
            game=body.game,
            bet_amount=body.bet_amount,
            server_seed=server_seed,
            client_seed=client_seed,
            nonce=nonce,
            bet_data=body.payload,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

    user.coins -= body.bet_amount
    if result.payout > 0:
        user.coins += result.payout

    user.total_wagered += body.bet_amount
    user.total_won += result.payout
    user.games_played += 1
    user.last_active_at = datetime.utcnow()

    row = await db.execute(insert(GameRound).values(
        user_id=user.id,
        game=body.game,
        bet_amount=body.bet_amount,
        payout=result.payout,
        multiplier=result.multiplier,
        outcome=result.outcome,
        payload=str(result.payload) if result.payload else None,
        server_seed=server_seed,
        client_seed=client_seed,
        nonce=nonce,
    ).returning(GameRound.id))
    round_id = row.scalar_one()

    await add_xp(db, user, settings.DAILY_BONUS, "bet")
    if result.payout > 0:
        await add_xp(db, user, 15, "win")

    await log_audit(db, user.id, "game.bet", target_user_id=user.id, metadata={"game": body.game, "bet": body.bet_amount, "payout": result.payout})

    return BetResult(
        game=body.game,
        bet_amount=body.bet_amount,
        payout=result.payout,
        multiplier=result.multiplier,
        outcome=result.outcome,
        new_balance=user.coins,
        round_id=round_id,
        payload=result.payload,
    )


class CashoutRequest(BaseModel):
    round_id: int
    multiplier: float


@router.post("/cashout", response_model=BetResult)
async def crash_cashout(body: CashoutRequest, user: CurrentUser, request: Request):
    db = request.state.db

    round_row = (await db.execute(
        select(GameRound).where(GameRound.id == body.round_id, GameRound.user_id == user.id)
    )).scalar_one_or_none()

    if not round_row or round_row.outcome != "pending":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid round")
    if round_row.game != "crash":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not a crash round")

    bet = round_row.bet_amount
    payout = int(bet * body.multiplier)
    user.coins += payout
    round_row.payout = payout
    round_row.multiplier = body.multiplier
    round_row.outcome = f"cashed@{body.multiplier:.2f}x"
    user.total_won += payout

    await add_xp(db, user, 15, "win")
    return BetResult(
        game="crash", bet_amount=bet, payout=payout, multiplier=body.multiplier,
        outcome=round_row.outcome, new_balance=user.coins, round_id=round_row.id, payload=None,
    )
