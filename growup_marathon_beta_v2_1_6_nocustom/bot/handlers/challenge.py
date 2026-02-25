from aiogram import Router, F
from datetime import date
from ..config import load_settings
from ..db import get_season, is_eliminated
from ..utils import now_tz, day_index
from ..texts import TASK_TEMPLATE

router = Router()
s = load_settings()

TASKS = [
    "🚶‍♂️ 10–20 daqiqa yurish yoki yengil mashq qiling.",
    "📚 20 daqiqa kitob o‘qing yoki foydali maqola o‘qing.",
    "📵 Telefonni 1 soat chetga qo‘ying va bitta ishni fokus bilan qiling.",
    "🧘 10 daqiqa stretching yoki plank/squat qiling.",
    "🧠 5 ta yangi so‘z o‘rganing va 3 ta gap tuzing.",
    "🧹 20 daqiqa tartib: xona/stol/toza joy.",
    "📝 Haftalik xulosa: 3 ta o‘rgangan narsangizni ayting."
]

@router.message(F.text.in_({"Bugungi task", "🗓 Bugungi task"}))
async def todays_task(m):
    season = await get_season()
    if not season[1] or not bool(season[4]):
        await m.answer("🕒 Challenge hali boshlanmagan.")
        return
    if await is_eliminated(m.from_user.id):
        await m.answer("⛔ Siz eliminatsiya bo‘lgansiz.")
        return
    tz_now = now_tz(s.tz)
    start = date.fromisoformat(season[1])
    di = day_index(start, tz_now.date())
    if di < 1:
        await m.answer("🕒 Challenge hali boshlanmagan.")
        return
    if di > s.beta_days:
        await m.answer("🏁 Challenge tugagan.")
        return
    await m.answer(TASK_TEMPLATE.format(day=di, total=s.beta_days, task=TASKS[di-1]))
