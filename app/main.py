from __future__ import annotations
import os
from dotenv import load_dotenv
from app.browser_scraper import get_availability_via_browser
from app.notifier import send_telegram

load_dotenv()

def getenv(key: str, default: str | None = None) -> str:
    v = os.getenv(key, default)
    if v is None or v == "":
        raise RuntimeError(f"Missing required env var: {key}")
    return v

def main() -> int:
    url        = os.getenv("TARGET_URL", "https://nimasdirang.com/Mountaineering-courses")
    row_match  = os.getenv("ROW_MATCH", "BMC-58")
    threshold  = int(os.getenv("THRESHOLD", "15"))
    bot_token  = getenv("TELEGRAM_BOT_TOKEN")
    chat_id    = getenv("TELEGRAM_CHAT_ID")

    value = get_availability_via_browser(url, row_match)

    print(f"{row_match} @ {url} → {value} (threshold {threshold})")
    if value < threshold:
        send_telegram(
            bot_token,
            chat_id,
            f"⚠️ {row_match} availability is {value} (< {threshold}).\n{url}"
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
