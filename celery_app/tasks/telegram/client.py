import httpx
import logging

logger = logging.getLogger(__name__)

class TelegramAPIClient:
	"""Синхронный клиент для Telegram Bot API"""

	def __init__(self, token: str, parse_mode: str = "HTML"):
		self.token = token
		self.base_url = "https://api.telegram.org"
		self.client = httpx.Client(timeout=30)
		self.parse_mode = parse_mode

	def request(self, method: str, **kwargs):
		url = f"{self.base_url}/bot{self.token}/{method}"
		kwargs.update({"parse_mode": self.parse_mode})

		response = self.client.post(url, json=kwargs)
		response.raise_for_status()
		return response.json()

	# def send_message(self, chat_id: int, text: str, **kwargs):
	# 	"""Синхронная отправка сообщения"""
	# 	kwargs.update({"chat_id": chat_id, "text": text})
	# 	return self.request(method="sendMessage", **kwargs)

	# def send_photo(self, chat_id: int, photo_url: str, **kwargs):
	# 	"""Синхронная отправка фото"""
	# 	kwargs.update({"chat_id": chat_id, "photo": photo_url})
	# 	return self.request(method="sendPhoto", **kwargs)

_clients: dict[str, TelegramAPIClient] = {}

def get_client(token: str) -> TelegramAPIClient:
	client = _clients.get(token)

	if client is None:
		client = TelegramAPIClient(token)
		_clients[token] = client

	return client
