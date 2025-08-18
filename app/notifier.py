"""Telegram notification module."""

from __future__ import annotations
import httpx

def send_telegram(bot_token: str, chat_id: str, text: str) -> None:
    """Send a message via Telegram bot API.
    
    Args:
        bot_token: The Telegram bot token for authentication.
        chat_id: The chat ID to send the message to.
        text: The message text to send.
        
    Raises:
        httpx.HTTPStatusError: If the Telegram API returns an error.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    with httpx.Client(timeout=15.0) as client:
        r = client.post(url, data=data)
        r.raise_for_status()
