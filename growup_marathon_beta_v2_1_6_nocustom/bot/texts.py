from __future__ import annotations

class E:
    wave = "👋"
    info = "ℹ️"
    sparkles = "✨"
    warning = "⚠️"
    fire = "🔥"
    check = "✅"
    trophy = "🏆"
    crown = "👑"


RULES = """📜 <b>Qoidalar</b>

1) Har kuni 1 ta vazifa bajariladi.
2) Vazifani isbot sifatida video yuborasiz.
3) Moderator(lar) videoni baholaydi.
4) Baholar leaderboard (reyting)ga tushadi.
5) Xushmuomalalik va spam yo‘q.
"""

WELCOME_TEXT = (
    f"{E.wave} Salom! Bu <b>GrowUp Marathon (BETA)</b> bot.\n\n"
    f"{E.info} Boshlash uchun /start ni bosing.\n"
    f"{E.sparkles} Qoidalar: /rules\n"
)

SUBSCRIBE_TEXT = (
    f"{E.warning} Botdan foydalanish uchun kanalga a’zo bo‘ling.\n\n"
    f"Keyin <b>Tekshirish</b> tugmasini bosing."
)

SUBSCRIBE_FAIL = (
    f"{E.warning} Siz hali kanalga a’zo bo‘lmagansiz.\n"
    f"Avval kanalga kiring, so‘ng <b>Tekshirish</b> tugmasini bosing."
)

ADMIN_ONLY = f"{E.warning} Bu bo‘lim faqat adminlar uchun."
MODERATOR_ONLY = f"{E.warning} Bu bo‘lim faqat moderatorlar uchun."

SUBMISSION_ASK_TEXT = (
    f"{E.fire} Vazifa videosini yuboring (video).\n"
    f"{E.info} Eslatma: videoni bitta xabar qilib yuboring, caption ixtiyoriy."
)

SUBMISSION_RECEIVED_TEXT = (
    f"{E.check} Qabul qilindi! Moderatorlar tekshiradi."
)

# Challenge (task) text template
TASK_TEMPLATE = (
    "🎯 <b>Bugungi vazifa</b>\n"
    "📅 Kun: {day}/{total}\n\n"
    "{task}\n\n"
    "📹 Video yuborish: /submit\n"
)

LEADERBOARD_TITLE = f"{E.trophy} <b>Leaderboard</b>"


def about(app_name: str) -> str:
    """About text shown in /about handler."""
    return (
        f"{E.info} <b>{app_name}</b>\n\n"
        f"{E.sparkles} GrowUp Marathon bot (BETA).\n"
        f"{E.fire} Har kuni vazifa: video yuborasiz, moderator baholaydi.\n"
        f"{E.crown} Reyting: /leaderboard\n"
    )
