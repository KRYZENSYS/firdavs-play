"""/admin handler — admin commands."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import settings

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Admins only.")
        return
    text = (
        "🛠 <b>Admin Commands</b>\n\n"
        "/stats — Bot statistics\n"
        "/broadcast — Send announcement (Web App)\n"
        "/ban — Ban a user (Web App)\n"
        "/coins — Adjust user coins (Web App)\n"
        "/promo — Create promo code (Web App)\n\n"
        "Open the Web App admin panel for the full UI."
    )
    await message.answer(text)
