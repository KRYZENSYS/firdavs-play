"""Pydantic schemas for API request/response."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    photo_url: str | None
    coins: int
    xp: int
    level: int
    games_played: int
    is_premium: bool
    created_at: datetime


class UserUpdate(BaseModel):
    language_code: str | None = Field(default=None, max_length=8)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserOut


class BetRequest(BaseModel):
    game: str
    bet_amount: int = Field(ge=10, le=100000)
    client_seed: str | None = None
    payload: dict | None = None


class BetResult(BaseModel):
    game: str
    bet_amount: int
    payout: int
    multiplier: float
    outcome: str
    new_balance: int
    round_id: int
    payload: dict | None = None


class GameRoundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    game: str
    bet_amount: int
    payout: int
    multiplier: float
    outcome: str
    created_at: datetime


class DailyBonusResult(BaseModel):
    claimed: bool
    coins_awarded: int
    streak: int
    next_available_at: datetime | None


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str | None
    first_name: str | None
    photo_url: str | None
    coins: int
    level: int
    xp: int


class MissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    title: str
    description: str
    type: str
    goal: int
    reward_coins: int
    progress: int
    completed: bool
    claimed: bool


class AchievementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    title: str
    description: str
    icon: str
    reward_coins: int
    unlocked_at: datetime | None


class InventoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_code: str
    item_type: str
    quantity: int
    acquired_at: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    title: str
    body: str
    read: bool
    created_at: datetime


class PromoRedeemRequest(BaseModel):
    code: str = Field(min_length=3, max_length=64)


class PromoRedeemResult(BaseModel):
    success: bool
    coins_awarded: int
    message: str
