from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from ..config import load_settings
from ..db import set_submission_rating, reject_submission, get_submission, get_pending_submissions
from ..keyboards import moderator_menu, rating_kb, main_menu
from ..db import get_leaderboard

router = Router()

def _is_mod(user_id: int) -> bool:
    s = load_settings()
    return user_id in s.moderator_ids or user_id in s.admin_ids

@router.message(Command("mod"))
async def mod_start(m: Message):
    if not _is_mod(m.from_user.id):
        return
    await m.answer("🛠 Moderator panel", reply_markup=moderator_menu())

@router.message(F.text == "🏠 Asosiy menu")
async def back_to_main(m: Message):
    if not _is_mod(m.from_user.id):
        return
    await m.answer("🏠", reply_markup=main_menu())

@router.message(F.text == "📝 Pending videolar")
async def list_pending(m: Message):
    if not _is_mod(m.from_user.id):
        return
    rows = await get_pending_submissions(limit=10)
    if not rows:
        await m.answer("✅ Pending video yo‘q.")
        return
    lines = ["🕒 <b>Pending videolar (top 10)</b>"]
    for sid, uid, day_index, dur, submitted_at in rows:
        lines.append(f"• ID <code>{sid}</code> | User <code>{uid}</code> | {day_index}-kun | {dur}s")
    await m.answer("\n".join(lines), parse_mode="HTML")

@router.message(F.text == "📊 Live Ranking")
async def live_ranking(m: Message):
    if not _is_mod(m.from_user.id):
        return
    board = await get_leaderboard(limit=10)
    if not board:
        await m.answer("Hali ishtirokchilar yo‘q.")
        return
    text = ["🏆 <b>Top 10</b>"]
    for i, (uid, full_name, total) in enumerate(board, start=1):
        text.append(f"{i}. {full_name} — <b>{total}</b> ball")
    await m.answer("\n".join(text), parse_mode="HTML")

@router.callback_query(F.data.startswith("rate:"))
async def rate_cb(c: CallbackQuery):
    if not _is_mod(c.from_user.id):
        await c.answer("Ruxsat yo‘q.", show_alert=True)
        return

    try:
        _, sid, score = c.data.split(":")
        sid_i = int(sid)
        score_i = int(score)
    except Exception:
        await c.answer("Callback xato.", show_alert=True)
        return

    ok = await set_submission_rating(sid_i, score_i, rated_by=c.from_user.id)
    if not ok:
        await c.answer("Bu video allaqachon baholangan yoki topilmadi.", show_alert=True)
        return

    sub = await get_submission(sid_i)
    # sub: id, user_id, day, file_id, dur, submitted_at, status, score, rated_by, rated_at, comment
    await c.message.edit_caption(
        (c.message.caption or "") + f"\n\n✅ Baholandi: <b>{score_i}</b> ball (mod: <code>{c.from_user.id}</code>)",
        reply_markup=None,
        parse_mode="HTML",
    )
    await c.answer("✅ Saqlandi")

    # Notify user
    try:
        await c.bot.send_message(
            chat_id=sub[1],
            text=f"✅ Video baholandi!\n📅 {sub[2]}-kun \n⭐️ Ball: <b>{score_i}</b>",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("reject:"))
async def reject_cb(c: CallbackQuery):
    if not _is_mod(c.from_user.id):
        await c.answer("Ruxsat yo‘q.", show_alert=True)
        return
    try:
        _, sid = c.data.split(":")
        sid_i = int(sid)
    except Exception:
        await c.answer("Callback xato.", show_alert=True)
        return

    ok = await reject_submission(sid_i, rated_by=c.from_user.id, comment="Rejected by moderator")
    if not ok:
        await c.answer("Bu video allaqachon ko‘rilgan yoki topilmadi.", show_alert=True)
        return

    sub = await get_submission(sid_i)
    await c.message.edit_caption(
        (c.message.caption or "") + f"\n\n❌ Rad etildi (mod: <code>{c.from_user.id}</code>)",
        reply_markup=None,
        parse_mode="HTML",
    )
    await c.answer("❌ Rad etildi")

    try:
        await c.bot.send_message(
            chat_id=sub[1],
            text=f"❌ Video rad etildi.\n📅 {sub[2]}-kun\nAgar xato bo‘lsa moderatorga yozing.",
            reply_markup=main_menu(),
        )
    except Exception:
        pass
