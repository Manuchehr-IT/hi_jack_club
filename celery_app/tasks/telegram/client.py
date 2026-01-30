import httpx
import logging
import os

logger = logging.getLogger(__name__)

class TelegramAPIClient:
    PARSE_MODE = "HTML"
    """Синхронный клиент для Telegram Bot API"""

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.client = httpx.Client(timeout=30)

    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()

    def send_message(self, chat_id: int, text: str, **kwargs):
        """Синхронная отправка сообщения"""
        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": self.PARSE_MODE,
            **kwargs
        }

        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def send_photo(self, chat_id: int, photo_url: str, caption: str = "", **kwargs):
        """Синхронная отправка фото"""
        url = f"{self.base_url}/sendPhoto"

        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": self.PARSE_MODE,
            **kwargs
        }

        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
