Grow Up Marathon Beta v2.0.0

What changed:
- ✅ Admin and Moderator roles are separated.
- ✅ Users submit videos, but **moderators** give the score (no auto-scoring).
- ✅ Moderators DO NOT need to forward anything to admin.

Setup
1) Create a bot with @BotFather and put BOT_TOKEN into .env
2) (Optional) Required channel:
   - If you use REQUIRED_CHANNEL as **chat id** (-100...), bot can check subscription, but the "Join" button can't be auto-made.
   - If you use REQUIRED_CHANNEL as **@username** or full https://t.me/... link, bot can show a proper "Join" button.
3) Copy .env.example to .env and fill values (see below)
4) Install deps:
   pip install -r requirements.txt
5) Run:
   python -m bot

.env important fields
- BOT_TOKEN=...
- ADMIN_IDS=123,456
- MODERATOR_IDS=111,222
- REQUIRED_CHANNEL=@your_channel   (optional)
- BETA_DAYS=7
- TIMEZONE=Asia/Tashkent

Admin commands:
- /admin
- /open_reg
- /close_reg
- /start_season
- /stop_season
- /lb
- /announce

Moderator panel:
- /mod
