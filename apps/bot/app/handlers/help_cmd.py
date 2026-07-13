"""/help handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router()


HELP_TEXT = (
    "📖 <b>Firdavs Play — Help</b>\n\n"
    "<b>Available commands:</b>\n"
    "/start — Open the Web App\n"
    "/balance — Show your coins, level, XP\n"
    "/daily — Daily bonus reminder\n"
    "/referral — Get your invite link\n"
    "/help — This help message\n\n"
    "<b>Games (in Web App):</b>\n"
    "🎮 Crash · Mines · Plinko · Dice · Coin Flip · Lucky Wheel\n"
    "🎯 Card Pick · Keno · Limbo · Hi-Lo · Towers · Jackpot · Wheel Duel\n\n"
    "💬 Support: @FirdavsSupport"
)


@router.message(Command("help"))
@router.callback_query(F.data == "help")
async def cmd_help(event: Message | CallbackQuery) -> None:
    if isinstance(event, CallbackQuery):
        await event.message.answer(HELP_TEXT)
        await event.answer()
    else:
        await event.answer(HELP_TEXT)
