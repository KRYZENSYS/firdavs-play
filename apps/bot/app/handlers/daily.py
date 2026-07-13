"""/daily handler — daily bonus claim reminder."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings

router = Router()


@router.message(Command("daily"))
@router.callback_query(F.data == "daily")
async def cmd_daily(event: Message | CallbackQuery) -> None:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Claim Daily Bonus", web_app=WebAppInfo(url=settings.WEBAPP_URL))]
    ])
    text = (
        "🎁 <b>Daily Bonus</b>\n\n"
        "Open the Web App to claim your <b>100 coin</b> daily reward.\n"
        "Don't miss it — the streak resets if you skip a day!"
    )
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)
