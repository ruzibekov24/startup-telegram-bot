from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def _normalize_tg_url(value: str) -> str:
    """InlineKeyboardButton(url=...) uchun Telegram URL ni to'g'rilaydi."""
    v = (value or "").strip()
    if not v:
        return ""

    # @channel -> https://t.me/channel
    if v.startswith("@"):  # username
        return f"https://t.me/{v[1:]}"

    # t.me/xxx -> https://t.me/xxx
    if v.startswith("t.me/") or v.startswith("telegram.me/"):
        return "https://" + v

    # already ok
    if v.startswith("http://") or v.startswith("https://"):
        return v

    # plain username
    return f"https://t.me/{v}"

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗓 Bugungi task"), KeyboardButton(text="🎥 Video topshirish")],
            [KeyboardButton(text="🏆 Live Ranking"), KeyboardButton(text="📈 Mening natijam")],
            [KeyboardButton(text="ℹ️ Challenge haqida"), KeyboardButton(text="📜 Qoidalar")],
        ],
        resize_keyboard=True
    )

def subscribe_kb(channel: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    raw = (channel or "").strip()
    url = _normalize_tg_url(raw)

    # Agar admin chat_id (-100...) berib yuborgan bo'lsa, URL tugma ishlamaydi.
    # Bu holatda xatoni foydalanuvchiga tushunarli qilib chiqaramiz.
    if raw.startswith("-100") or raw.lstrip("-").isdigit() or not url:
        b.button(text="🔔 Kanal havolasini sozlash kerak", callback_data="bad_channel_link")
    else:
        b.button(text="🔔 Obuna bo'lish", url=url)
    b.button(text="✅ Tasdiqlash", callback_data="confirm_sub")
    b.adjust(1)
    return b.as_markup()

def announce_button_kb(text: str, url: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=text, url=_normalize_tg_url(url))
    return b.as_markup()


def rating_kb(submission_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    # 0-3 ball: xohlasangiz o'zgartirasiz
    b.button(text="0️⃣", callback_data=f"rate:{submission_id}:0")
    b.button(text="1️⃣", callback_data=f"rate:{submission_id}:1")
    b.button(text="2️⃣", callback_data=f"rate:{submission_id}:2")
    b.button(text="3️⃣", callback_data=f"rate:{submission_id}:3")
    b.button(text="❌ Rad etish", callback_data=f"reject:{submission_id}")
    b.adjust(4, 1)
    return b.as_markup()

def moderator_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Pending videolar"), KeyboardButton(text="📊 Live Ranking")],
            [KeyboardButton(text="🏠 Asosiy menu")],
        ],
        resize_keyboard=True
    )
