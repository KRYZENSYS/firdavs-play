"""Firdavs Play Telegram bot main entry."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.handlers import start, balance, daily, referral, admin, help_cmd

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    if not settings.BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(balance.router)
    dp.include_router(daily.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)
    dp.include_router(help_cmd.router)

    me = await bot.get_me()
    print(f"Bot @{me.username} is up. WebApp: {settings.WEBAPP_URL}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
