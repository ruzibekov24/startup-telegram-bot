from aiogram import Router, F
from ..db import get_leaderboard

router = Router()

@router.message(F.text.in_({"Live Ranking", "🏆 Live Ranking"}))
async def lb(m):
    rows = await get_leaderboard(20)
    if not rows:
        await m.answer("Hali ma'lumot yo'q.")
        return
    text = "<b>Live Ranking</b>\n━━━━━━━━━━━━━━━\n"
    for i, (_, name, total) in enumerate(rows, start=1):
        if i == 1:
            p = "🥇"
        elif i == 2:
            p = "🥈"
        elif i == 3:
            p = "🥉"
        else:
            p = f"{i}."
        text += f"{p} {name}  <b>{total}</b>\n"
    await m.answer(text)
