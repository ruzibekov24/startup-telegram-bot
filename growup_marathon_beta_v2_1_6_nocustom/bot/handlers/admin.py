from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date, timedelta
from ..config import load_settings
from ..db import set_season_dates, set_running, set_registration, get_leaderboard, create_announcement, set_announcement_message_id
from ..states import AnnounceState
from ..keyboards import announce_button_kb

router = Router()
s = load_settings()

def is_admin(user_id: int) -> bool:
    return user_id in s.admin_ids

def confirm_kb():
    b = InlineKeyboardBuilder()
    b.button(text="📣 Post qilish", callback_data="ann_post")
    b.button(text="❌ Bekor qilish", callback_data="ann_cancel")
    b.adjust(1)
    return b.as_markup()

@router.message(F.text == "/admin")
async def admin_help(m):
    if not is_admin(m.from_user.id):
        return
    await m.answer(
        "<b>Admin panel</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "/open_reg\n"
        "/close_reg\n"
        "/start_season\n"
        "/stop_season\n"
        "/lb\n"
        "/announce"
    )

@router.message(F.text == "/open_reg")
async def open_reg(m):
    if not is_admin(m.from_user.id):
        return
    await set_registration(True)
    await m.answer("✅ Ro'yxatdan o'tish ochildi.")

@router.message(F.text == "/close_reg")
async def close_reg(m):
    if not is_admin(m.from_user.id):
        return
    await set_registration(False)
    await m.answer("⛔ Ro'yxatdan o'tish yopildi.")

@router.message(F.text == "/start_season")
async def start_season(m):
    if not is_admin(m.from_user.id):
        return
    start = date.today()
    end = start + timedelta(days=s.beta_days-1)
    await set_season_dates(start.isoformat(), end.isoformat())
    await set_running(True)
    await set_registration(False)
    await m.answer(f"🚀 Season boshlandi: <code>{start.isoformat()}</code> → <code>{end.isoformat()}</code>")

@router.message(F.text == "/stop_season")
async def stop_season(m):
    if not is_admin(m.from_user.id):
        return
    await set_running(False)
    await m.answer("🛑 Season to'xtatildi.")

@router.message(F.text == "/lb")
async def lb(m):
    if not is_admin(m.from_user.id):
        return
    rows = await get_leaderboard(20)
    if not rows:
        await m.answer("Hali ma'lumot yo'q.")
        return
    text = "<b>Leaderboard</b>\n━━━━━━━━━━━━━━━\n"
    for i, (_, name, total) in enumerate(rows, start=1):
        text += f"{i}. {name} - <b>{total}</b>\n"
    await m.answer(text)

@router.message(F.text == "/announce")
async def ann_start(m, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    await state.set_state(AnnounceState.waiting_text)
    await m.answer("📝 E'lon matnini yuboring.")

@router.message(AnnounceState.waiting_text)
async def ann_text(m, state: FSMContext):
    if not is_admin(m.from_user.id):
        await state.clear()
        return
    await state.update_data(text=m.text)
    await state.set_state(AnnounceState.waiting_button_text)
    await m.answer("🔘 Tugma nomini yuboring (yoki '-' yuboring).")

@router.message(AnnounceState.waiting_button_text)
async def ann_btn_text(m, state: FSMContext):
    if not is_admin(m.from_user.id):
        await state.clear()
        return
    t = m.text.strip()
    if t == "-":
        await state.update_data(button_text=None, button_url=None)
        data = await state.get_data()
        await state.set_state(AnnounceState.waiting_confirm)
        await m.answer(data["text"], reply_markup=confirm_kb())
        return
    await state.update_data(button_text=t)
    await state.set_state(AnnounceState.waiting_button_url)
    await m.answer("🔗 Tugma URL yuboring (https:// yoki t.me/...).")

@router.message(AnnounceState.waiting_button_url)
async def ann_btn_url(m, state: FSMContext):
    if not is_admin(m.from_user.id):
        await state.clear()
        return
    await state.update_data(button_url=m.text.strip())
    data = await state.get_data()
    await state.set_state(AnnounceState.waiting_confirm)
    await m.answer(data["text"], reply_markup=confirm_kb())

@router.callback_query(F.data.in_({"ann_post","ann_cancel"}))
async def ann_decide(c, state: FSMContext, bot: Bot):
    if not is_admin(c.from_user.id):
        await state.clear()
        await c.answer()
        return
    if c.data == "ann_cancel":
        await state.clear()
        await c.message.edit_text("❌ Bekor qilindi.")
        await c.answer()
        return
    data = await state.get_data()
    text = data.get("text", "")
    btn_text = data.get("button_text")
    btn_url = data.get("button_url")
    ann_id = await create_announcement(c.from_user.id, text, btn_text, btn_url)
    if not s.channel_announce_id:
        await c.message.edit_text("CHANNEL_ANNOUNCE_ID sozlanmagan.")
        await state.clear()
        await c.answer()
        return
    reply_markup = None
    if btn_text and btn_url:
        reply_markup = announce_button_kb(btn_text, btn_url)
    msg = await bot.send_message(chat_id=s.channel_announce_id, text=text, reply_markup=reply_markup)
    await set_announcement_message_id(ann_id, msg.message_id)
    await c.message.edit_text("✅ Kanalga joylandi.")
    await state.clear()
    await c.answer()
