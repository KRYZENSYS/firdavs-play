"""/referral handler — generate referral link."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.config import settings

router = Router()


def make_referral_link(user_id: int) -> str:
    return f"https://t.me/{settings.BOT_USERNAME}?start=ref_{user_id}"


@router.message(Command("referral"))
@router.callback_query(F.data == "referral")
async def cmd_referral(event: Message | CallbackQuery) -> None:
    user_id = event.from_user.id
    link = make_referral_link(user_id)
    text = (
        "👥 <b>Invite Friends & Earn Coins</b>\n\n"
        "Share your link below. For every friend who joins via your link, "
        "<b>you both get 500 coins</b>!\n\n"
        f"🔗 <code>{link}</code>\n\n"
        "Open the Web App to track your referrals."
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(text)
        await event.answer()
    else:
        await event.answer(text)
