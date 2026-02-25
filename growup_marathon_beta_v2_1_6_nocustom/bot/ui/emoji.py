from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Emoji:
    """Small helper to render Telegram custom (premium) emojis safely in HTML mode.

    If an emoji-id is not configured, it falls back to a normal unicode emoji.
    """
    ids: dict[str, str]

    def tg(self, key: str, fallback: str) -> str:
        eid = (self.ids or {}).get(key)
        if eid and str(eid).isdigit():
            # Telegram requires some visible fallback char inside the tag.
            return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'
        return fallback

    # Common shortcuts used in texts
    @property
    def wave(self) -> str: return self.tg("wave", "👋")
    @property
    def sparkles(self) -> str: return self.tg("sparkles", "✨")
    @property
    def fire(self) -> str: return self.tg("fire", "🔥")
    @property
    def trophy(self) -> str: return self.tg("trophy", "🏆")
    @property
    def info(self) -> str: return self.tg("info", "ℹ️")
    @property
    def check(self) -> str: return self.tg("check", "✅")
    @property
    def warning(self) -> str: return self.tg("warning", "⚠️")
