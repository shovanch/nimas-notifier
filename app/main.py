from __future__ import annotations
import os
from dotenv import load_dotenv

from app.scrape import get_availability
from app.notifier import send_telegram

load_dotenv()

def getenv_required(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Missing required env var: {key}")
    return v

def main() -> int:
    page_url  = os.getenv("TARGET_URL")
    api_url   = os.getenv("NIMAS_API_URL")
    serial_no = os.getenv("ROW_MATCH")
    threshold = int(os.getenv("THRESHOLD"))
    backend   = os.getenv("SCRAPER_BACKEND", "auto")  # api | playwright | auto

    bot_token = getenv_required("TELEGRAM_BOT_TOKEN")
    chat_id   = getenv_required("TELEGRAM_CHAT_ID")

    value = get_availability(page_url, api_url, serial_no, backend)
    print(f"{serial_no} → {value} (threshold {threshold}) via {backend}")

    if value < threshold:
        send_telegram(
            bot_token,
            chat_id,
            f"⚠️ {serial_no} availability is {value} (< {threshold}).\n{page_url}"
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
