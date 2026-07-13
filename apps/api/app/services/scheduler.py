"""Background scheduler for daily bonus, leaderboard reset, and reminders."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

log = structlog.get_logger()

scheduler = AsyncIOScheduler(timezone="UTC")


@scheduler.scheduled_job(CronTrigger(hour=0, minute=0))
async def daily_reset_job() -> None:
    """Reset daily missions and notify users at midnight UTC."""
    log.info("scheduler.daily_reset.start")
    try:
        from app.services.daily_bonus import reset_daily_missions
        await reset_daily_missions()
    except Exception as e:
        log.error("scheduler.daily_reset.error", error=str(e))
    log.info("scheduler.daily_reset.done")


@scheduler.scheduled_job(CronTrigger(day_of_week="mon", hour=0, minute=0))
async def weekly_reset_job() -> None:
    """Reset weekly missions every Monday."""
    log.info("scheduler.weekly_reset.start")
    try:
        from app.services.daily_bonus import reset_weekly_missions
        await reset_weekly_missions()
    except Exception as e:
        log.error("scheduler.weekly_reset.error", error=str(e))
    log.info("scheduler.weekly_reset.done")


@scheduler.scheduled_job(CronTrigger(hour=12, minute=0))
async def daily_bonus_reminder_job() -> None:
    """Send daily bonus reminders at 12:00 UTC."""
    log.info("scheduler.daily_reminder.start")
    try:
        from app.services.daily_bonus import send_daily_reminders
        await send_daily_reminders()
    except Exception as e:
        log.error("scheduler.daily_reminder.error", error=str(e))
    log.info("scheduler.daily_reminder.done")
