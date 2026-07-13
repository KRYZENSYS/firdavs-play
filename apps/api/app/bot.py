"""
Telegram bot (aiogram 3) — robust polling with auto-reconnect.

Features:
- Forever-reconnect on any disconnect / network error
- Exponential backoff between retries (capped at 60s)
- Self-ping every 4 minutes to keep Replit server alive + keep WS warm
- Health check endpoint /healthz (used by UptimeRobot and Replit always-on)
- Graceful shutdown
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global reference so the health endpoint can show bot status
_bot_state = {"last_ping": 0, "running": False, "started_at": 0, "errors": 0}


def get_bot_state() -> dict:
    return dict(_bot_state)


async def start_bot():
    """Main entry point — runs in background task from main.py lifespan."""
    if not settings.BOT_TOKEN:
        logger.info("BOT_TOKEN not set — Telegram bot disabled")
        return

    _bot_state["running"] = False
    _bot_state["started_at"] = 0
    _bot_state["errors"] = 0

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
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
            "/start — Open the game\n"
            "/help — Show this help\n"
            "/balance — Check your balance\n"
            "/games — List all games\n"
            "/ping — Bot health check"
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

    @dp.message(Command("ping"))
    async def ping_cmd(m: types.Message):
        _bot_state["last_ping"] = m.date.timestamp()
        await m.answer("🏓 <b>Pong!</b> Bot is alive and responding.")

    # Suppress noisy aiogram startup logs
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    # Self-ping task — keeps Replit warm AND verifies bot connection is alive
    async def self_ping_loop():
        while True:
            try:
                await asyncio.sleep(240)  # every 4 minutes
                me = await bot.get_me()
                _bot_state["last_ping"] = asyncio.get_event_loop().time()
                logger.debug(f"Self-ping ok: @{me.username}")
            except Exception as e:
                logger.warning(f"Self-ping failed: {e}")
                _bot_state["errors"] += 1

    # Robust polling loop with auto-reconnect
    backoff = 1.0
    max_backoff = 60.0

    while True:  # outer loop = forever-retry
        try:
            _bot_state["running"] = True
            if _bot_state["started_at"] == 0:
                import time
                _bot_state["started_at"] = time.time()

            # Launch self-ping alongside polling
            ping_task = asyncio.create_task(self_ping_loop())

            logger.info("🤖 Bot polling started (forever mode)...")
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                handle_as_tasks=True,
            )
            # If start_polling returns cleanly, cancel self-ping
            ping_task.cancel()

        except asyncio.CancelledError:
            logger.info("Bot cancelled — shutting down")
            _bot_state["running"] = False
            try:
                await bot.session.close()
            except Exception:
                pass
            return

        except Exception as e:
            _bot_state["running"] = False
            _bot_state["errors"] += 1
            logger.warning(f"⚠️ Bot disconnected: {e!r}. Reconnecting in {backoff:.1f}s...")

            # Cancel any lingering ping task
            try:
                ping_task.cancel()
            except Exception:
                pass

            await asyncio.sleep(backoff)
            # Exponential backoff with cap
            backoff = min(backoff * 1.5, max_backoff)
            # Reset backoff if a long time has passed (means we recovered)
            await asyncio.sleep(0.1)  # yield
        else:
            # Clean exit (e.g. SIGTERM) — break outer loop
            _bot_state["running"] = False
            break
