"""/start handler with WebApp launch button."""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings

router = Router()


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Open Firdavs Play", web_app=WebAppInfo(url=settings.WEBAPP_URL))],
        [InlineKeyboardButton(text="💰 Balance", callback_data="balance"),
         InlineKeyboardButton(text="🎁 Daily Bonus", callback_data="daily")],
        [InlineKeyboardButton(text="👥 Invite Friends", callback_data="referral"),
         InlineKeyboardButton(text="📖 Help", callback_data="help")],
    ])

    text = (
        f"👋 <b>Welcome to Firdavs Play!</b>\n\n"
        f"🎮 13 premium games\n"
        f"💎 Earn coins & XP\n"
        f"🏆 Compete on the global leaderboard\n"
        f"🎁 Daily bonus & referral rewards\n\n"
        f"👇 Tap the button to launch the Web App"
    )
    await message.answer(text, reply_markup=kb)


@router.message(CommandStart(deep_link=True))
async def cmd_start_referral(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    ref_code = args[1] if len(args) > 1 else None
    ref_param = f"?ref={ref_code.replace('ref_', '')}" if ref_code and ref_code.startswith("ref_") else ""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Open & Claim Bonus", web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}{ref_param}"))],
    ])

    await message.answer(
        "🎁 <b>You were invited by a friend!</b>\n\n"
        "Open the Web App to claim your <b>500 coin</b> welcome bonus.",
        reply_markup=kb,
    )
