from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from ..config import load_settings
from ..keyboards import subscribe_kb, main_menu
from ..texts import SUBSCRIBE_TEXT, SUBSCRIBE_FAIL
from ..db import upsert_user

router = Router()
s = load_settings()

async def check_sub(bot: Bot, user_id: int) -> bool:
    if not s.required_channel:
        return True
    ch = s.required_channel.strip()
    if ch.startswith("https://t.me/"):
        ch = "@" + ch.split("https://t.me/")[1].split("/")[0]
    try:
        m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
        return m.status in {"member", "administrator", "creator"}
    except Exception:
        return False

@router.message(F.text == "/start")
async def start(m: Message, bot: Bot):
    await upsert_user(m.from_user.id, m.from_user.username, m.from_user.full_name)
    ok = await check_sub(bot, m.from_user.id)
    if ok:
        await m.answer("✅ Menyu ochildi", reply_markup=main_menu())
    else:
        await m.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_kb(s.required_channel))

@router.callback_query(F.data == "confirm_sub")
async def confirm(c: CallbackQuery, bot: Bot):
    ok = await check_sub(bot, c.from_user.id)
    if ok:
        await c.message.edit_text("✅ Tasdiqlandi")
        await c.message.answer("✅ Menyu", reply_markup=main_menu())
        await c.answer()
    else:
        await c.answer(SUBSCRIBE_FAIL, show_alert=True)


@router.callback_query(F.data == "bad_channel_link")
async def bad_channel_link(c: CallbackQuery):
    # admin config xatosi: REQUIRED_CHANNEL chat_id bo'lib qolgan.
    await c.answer(
        "Admin sozlamasida kanal havolasi noto'g'ri. \n"
        "REQUIRED_CHANNEL ni @kanal_username yoki https://t.me/... qilib yozing.",
        show_alert=True,
    )
