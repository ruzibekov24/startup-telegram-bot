from aiogram import Router, F
from ..config import load_settings
from ..db import get_season, is_eliminated, get_total_score, get_warning_count, get_pending_count
from ..texts import about, RULES

router = Router()
@router.message(F.text.in_({"Challenge haqida", "ℹ️ Challenge haqida"}))
async def about_h(m):
    s = load_settings()
    await m.answer(about(s.app_name))

@router.message(F.text.in_({"Qoidalar", "📜 Qoidalar"}))
async def rules(m):
    await m.answer(RULES)

@router.message(F.text.in_({"Mening natijam", "📈 Mening natijam"}))
async def profile(m):
    elim = await is_eliminated(m.from_user.id)
    total = await get_total_score(m.from_user.id)
    warn = await get_warning_count(m.from_user.id)
    season = await get_season()
    running = bool(season[4])
    status = "⛔ Eliminatsiya" if elim else "✅ Faol"
    if not running and not elim:
        status = "🕒 Kutilmoqda"
    pending = await get_pending_count(m.from_user.id)
    await m.answer(
        "<b>Mening natijam</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"👤 <b>Status:</b> {status}\n"
        f"⭐ <b>Ball:</b> <b>{total}</b>\n"
        f"⏳ <b>Pending:</b> <b>{pending}</b>\n"
        f"⚠️ <b>Warning:</b> <b>{warn}</b>"
    )
