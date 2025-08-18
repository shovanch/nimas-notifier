"""Telegram notification module."""

import httpx


def send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    """Send message via Telegram bot API."""
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': True}
    with httpx.Client(timeout=15.0) as client:
        r = client.post(url, data=data)
        r.raise_for_status()
