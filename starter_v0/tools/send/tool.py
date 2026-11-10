from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _is_confirmed(value: Any) -> bool:
    # Bug fix: models sometimes send booleans as strings. `not "false"` is False, so the old
    # `if not confirmed` check let confirmed="false" through and posted to Telegram.
    if isinstance(value, bool):
        return value
    return isinstance(value, str) and value.strip().lower() == "true"


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not _is_confirmed(confirmed):
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return {"tool": "send_telegram", "status": "sent"}
    except Exception as exc:
        return err("send_telegram", exc)

