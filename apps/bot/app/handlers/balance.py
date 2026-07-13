"""/balance handler — show user balance via API."""
import aiohttp
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import settings

router = Router()


async def fetch_user(telegram_id: int) -> dict | None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{settings.API_URL}/api/v1/auth/dev",
                json={"telegram_id": telegram_id, "first_name": "Player"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as r:
                if r.status == 200:
                    return await r.json()
    except Exception:
        return None
    return None


@router.message(Command("balance"))
@router.callback_query(F.data == "balance")
async def cmd_balance(event: Message | CallbackQuery) -> None:
    target = event.from_user
    data = await fetch_user(target.id)
    if not data:
        msg = "⚠️ Could not load your profile. Please open the Web App first."
        if isinstance(event, CallbackQuery):
            await event.answer(msg, show_alert=True)
        else:
            await event.answer(msg)
        return

    user = data.get("user", {})
    text = (
        f"💰 <b>Your Balance</b>\n\n"
        f"👤 {user.get('first_name') or 'Player'} {('@' + user['username']) if user.get('username') else ''}\n"
        f"🪙 Coins: <b>{user.get('coins', 0):,}</b>\n"
        f"⭐ Level: <b>{user.get('level', 1)}</b>\n"
        f"📈 XP: <b>{user.get('xp', 0):,}</b>\n"
        f"🎮 Games: <b>{user.get('games_played', 0)}</b>"
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)
