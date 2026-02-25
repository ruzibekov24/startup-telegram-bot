import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from .config import load_settings
from .db import init_db
from .scheduler import setup_scheduler
from .handlers import gate, user, challenge, submission, leaderboard, admin, moderator

async def main():
    s = load_settings()
    if not s.bot_token:
        raise RuntimeError("BOT_TOKEN missing")
    await init_db()
    # aiogram >= 3.7: parse_mode Bot() ichidan olib tashlangan.
    bot = Bot(token=s.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(gate.router)
    dp.include_router(user.router)
    dp.include_router(challenge.router)
    dp.include_router(submission.router)
    dp.include_router(leaderboard.router)
    dp.include_router(admin.router)
    dp.include_router(moderator.router)
    sched = setup_scheduler(s.tz, s.deadline_hour, s.deadline_minute, s.beta_days)
    sched.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
