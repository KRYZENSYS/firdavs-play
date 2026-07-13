"""Telegram bot (aiogram 3, polling mode)."""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

from app.core.config import settings

logger = logging.getLogger(__name__)


async def start_bot():
    if not settings.BOT_TOKEN:
        return
    bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start_cmd(m: types.Message):
        args = m.text.split(maxsplit=1)
        webapp_url = settings.WEBAPP_URL

        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="🎮 Open Game",
                web_app=types.WebAppInfo(url=webapp_url),
            )],
            [types.InlineKeyboardButton(
                text="👥 Invite Friends",
                url=f"https://t.me/share/url?url=https://t.me/{settings.BOT_USERNAME}?startapp=ref_{m.from_user.id}",
            )],
        ])
        await m.answer(
            "🎮 <b>Welcome to Firdavs Play!</b>\n\n"
            "🚀 13 Premium Games\n"
            "💰 Daily bonus & referral rewards\n"
            "⚡ Provably fair gaming\n\n"
            "Tap below to start playing 👇",
            reply_markup=kb,
        )

    @dp.message(Command("help"))
    async def help_cmd(m: types.Message):
        await m.answer(
            "🎮 <b>Firdavs Play Commands:</b>\n\n"
            "/start - Open the game\n"
            "/help - Show this help\n"
            "/balance - Check your balance\n"
            "/games - List all games"
        )

    @dp.message(Command("balance"))
    async def balance_cmd(m: types.Message):
        await m.answer(f"💰 Check your balance: {settings.WEBAPP_URL}")

    @dp.message(Command("games"))
    async def games_cmd(m: types.Message):
        await m.answer(
            "🎮 <b>Available Games:</b>\n\n"
            "🚀 Crash • 💣 Mines • 🎯 Plinko\n"
            "🎲 Dice • 🪙 Coin Flip • 🎡 Wheel\n"
            "🃏 Card Pick • 🔢 Keno • 📈 Limbo\n"
            "🎴 Hi-Lo • 🗼 Towers\n\n"
            f"Open: {settings.WEBAPP_URL}"
        )

    try:
        logger.info("Starting Telegram bot in polling mode...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        await bot.session.close()
