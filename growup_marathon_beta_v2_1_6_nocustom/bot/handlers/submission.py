from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, date

from ..config import load_settings
from ..db import create_submission, is_eliminated, get_season
from ..keyboards import main_menu, rating_kb
from ..texts import SUBMISSION_ASK_TEXT

router = Router()

def _format_duration(sec: int) -> str:
    m = sec // 60
    s = sec % 60
    return f"{m:02d}:{s:02d}"

@router.message(F.text.in_({"Video topshirish", "🎥 Video topshirish"}))
async def ask_submission(m: Message):
    s = load_settings()
    season = await get_season()
    if not season[4]:
        await m.answer("⛔️ Hozir marafon ishlamayapti.", reply_markup=main_menu())
        return
    if await is_eliminated(m.from_user.id):
        await m.answer("⛔️ Siz marafondan chetlatilgansiz.", reply_markup=main_menu())
        return
    await m.answer(SUBMISSION_ASK_TEXT)

@router.message(F.video)
async def receive_video(m: Message):
    s = load_settings()
    # beta: season length = beta_days (paid_days is for future monetization)
    season = await get_season()
    start_date = season[1]
    end_date = season[2]
    is_running = bool(season[4])
    if not (is_running and start_date and end_date):
        await m.answer("⛔️ Hozir marafon ishlamayapti.", reply_markup=main_menu())
        return

    if await is_eliminated(m.from_user.id):
        await m.answer("⛔️ Siz marafondan chetlatilgansiz.", reply_markup=main_menu())
        return

    today = date.today()
    start = date.fromisoformat(start_date)
    day_index = (today - start).days + 1
    if day_index < 1 or day_index > s.beta_days:
        await m.answer("⏳ Hozirgi kun marafon oralig'ida emas.", reply_markup=main_menu())
        return

    video = m.video
    duration_sec = int(video.duration or 0)
    file_id = video.file_id
    submitted_at = datetime.utcnow().isoformat()

    submission_id = await create_submission(m.from_user.id, day_index, file_id, duration_sec, submitted_at)
    if submission_id is None:
        await m.answer("⚠️ Bugungi kun uchun video allaqachon topshirilgansiz.", reply_markup=main_menu())
        return

    # User confirmation
    await m.answer(
        f"✅ Video qabul qilindi!\n\n"
        f"📅 Kun: <b>{day_index}-kun</b>\n"
        f"⏱ Davomiylik: <b>{_format_duration(duration_sec)}</b>\n\n"
        f"🕵️‍♂️ Moderatorlar baholaydi va ball keyinroq chiqadi.",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )

    # Send to moderators
    if not s.moderator_ids:
        # If no moderators configured, at least don't crash.
        await m.answer("⚠️ Moderatorlar ro'yxati sozlanmagan (MODERATOR_IDS). Ball berilmaydi.")
        return

    caption = (
        f"🆕 <b>Yangi video</b>\n"
        f"👤 User: <a href='tg://user?id={m.from_user.id}'>{m.from_user.full_name}</a>\n"
        f"🆔 ID: <code>{m.from_user.id}</code>\n"
        f"📅 Kun: <b>{day_index}-kun</b>\n"
        f"⏱ Davomiylik: <b>{_format_duration(duration_sec)}</b>\n\n"
        f"👇 Ballni tanlang:"
    )

    for mod_id in s.moderator_ids:
        try:
            await m.bot.send_video(
                chat_id=mod_id,
                video=file_id,
                caption=caption,
                reply_markup=rating_kb(submission_id),
                parse_mode="HTML",
            )
        except Exception:
            # ignore single moderator failures
            pass
