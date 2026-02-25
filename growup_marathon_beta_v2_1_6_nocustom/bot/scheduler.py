from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date
import pytz
import aiosqlite
from .db import get_season, inc_warning, eliminate, DB_PATH

async def deadline_job(tz_name: str, beta_days: int):
    season = await get_season()
    start_date = season[1]
    end_date = season[2]
    is_running = bool(season[4])
    if not (is_running and start_date and end_date):
        return
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    start = date.fromisoformat(start_date)
    di = (now.date() - start).days + 1
    if di < 1 or di > beta_days:
        return
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            SELECT u.user_id
            FROM users u
            LEFT JOIN submissions s ON s.user_id=u.user_id AND s.day_index=?
            LEFT JOIN eliminations e ON e.user_id=u.user_id
            WHERE u.is_active=1 AND e.user_id IS NULL AND s.id IS NULL
            """,
            (di,),
        )
        users = await cur.fetchall()
    for (user_id,) in users:
        wc = await inc_warning(user_id)
        if wc >= 2:
            await eliminate(user_id, "2 marta deadline o'tkazildi")

def setup_scheduler(tz_name: str, deadline_hour: int, deadline_minute: int, beta_days: int) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone=tz_name)
    minute = deadline_minute + 1
    hour = deadline_hour
    if minute >= 60:
        minute -= 60
        hour = (hour + 1) % 24
    sched.add_job(deadline_job, "cron", hour=hour, minute=minute, args=[tz_name, beta_days])
    return sched
