"""Seed default missions, achievements, and starter promo codes on first run."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Achievement, Mission, PromoCode


DEFAULT_MISSIONS = [
    {"code": "daily_play_3",   "title": "Play 3 games",                "description": "Play any 3 games today",                   "type": "daily",  "goal": 3,   "reward_coins": 50,  "reward_xp": 20},
    {"code": "daily_wager_500","title": "Wager 500 coins",              "description": "Wager a total of 500 coins",                "type": "daily",  "goal": 500, "reward_coins": 75,  "reward_xp": 25},
    {"code": "daily_win_1",    "title": "Win a round",                 "description": "Win any single game",                      "type": "daily",  "goal": 1,   "reward_coins": 30,  "reward_xp": 15},
    {"code": "weekly_play_25", "title": "Play 25 games",               "description": "Play 25 games this week",                  "type": "weekly", "goal": 25,  "reward_coins": 500, "reward_xp": 200},
    {"code": "weekly_wager_5k","title": "Wager 5000 coins",             "description": "Wager a total of 5000 coins this week",     "type": "weekly", "goal": 5000, "reward_coins": 750, "reward_xp": 300},
]

DEFAULT_ACHIEVEMENTS = [
    {"code": "first_bet",       "title": "First Bet",         "description": "Place your first bet",            "icon": "play",    "reward_coins": 50,   "condition_type": "games_played", "condition_value": 1},
    {"code": "veteran_10",      "title": "Veteran",           "description": "Play 10 games",                  "icon": "shield",  "reward_coins": 100,  "condition_type": "games_played", "condition_value": 10},
    {"code": "high_roller_100", "title": "High Roller",       "description": "Play 100 games",                 "icon": "crown",   "reward_coins": 1000, "condition_type": "games_played", "condition_value": 100},
    {"code": "whale_1000",      "title": "Whale",             "description": "Wager 10,000 coins total",       "icon": "whale",   "reward_coins": 2000, "condition_type": "wagered",     "condition_value": 10000},
    {"code": "lucky_streak",    "title": "Lucky Streak",      "description": "Win 5 games in a row",           "icon": "clover",  "reward_coins": 500,  "condition_type": "win_streak",  "condition_value": 5},
    {"code": "level_5",         "title": "Rising Star",       "description": "Reach level 5",                  "icon": "star",    "reward_coins": 200,  "condition_type": "level",       "condition_value": 5},
    {"code": "level_10",        "title": "Pro Player",        "description": "Reach level 10",                 "icon": "star2",   "reward_coins": 500,  "condition_type": "level",       "condition_value": 10},
]

DEFAULT_PROMO_CODES = [
    {"code": "WELCOME100",   "reward_coins": 100,   "max_uses": 10000},
    {"code": "FIRDAVS2026",  "reward_coins": 1000,  "max_uses": 1000},
    {"code": "PREMIUM500",   "reward_coins": 500,   "max_uses": 500},
]


async def seed_defaults(db: AsyncSession) -> None:
    existing = (await db.execute(select(Mission).limit(1))).scalar_one_or_none()
    if not existing:
        for m in DEFAULT_MISSIONS:
            db.add(Mission(**m))

    existing = (await db.execute(select(Achievement).limit(1))).scalar_one_or_none()
    if not existing:
        for a in DEFAULT_ACHIEVEMENTS:
            db.add(Achievement(**a))

    existing = (await db.execute(select(PromoCode).limit(1))).scalar_one_or_none()
    if not existing:
        for p in DEFAULT_PROMO_CODES:
            db.add(PromoCode(**p, is_active=True))
