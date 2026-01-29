import hashlib
import hmac
import httpx
import json
import time
import urllib
from django.conf import settings
from django.core.files.base import ContentFile
from typing import Dict, Any

from .schemas import TelegramUser, TelegramChat, TelegramInitData
from .exceptions import InvalidTelegramDataError, ExpiredTelegramDataError

import logging
logger = logging.getLogger()


def parse_telegram_init_data(raw_data: str) -> TelegramInitData:
	"""
	Парсит и валидирует Telegram init_data
	Возвращает готовый объект TelegramInitData
	"""
	try:
		parsed_data = _validate_and_parse_raw_data(raw_data)

		return TelegramInitData(
			query_id=parsed_data.get("query_id"),
			auth_date=int(parsed_data.get("auth_date", 0)),
			hash=parsed_data.get("hash"),
			start_param=parsed_data.get("start_param"),
			user=TelegramUser(**parsed_data["user"]) if "user" in parsed_data else None,
			chat=TelegramChat(**parsed_data["chat"]) if "chat" in parsed_data else None,
		)
	except ValueError as e:
		raise InvalidTelegramDataError(str(e))
	except Exception as e:
		raise InvalidTelegramDataError(f"Unexpected error: {str(e)}")

def _validate_and_parse_raw_data(raw_data: str) -> Dict[str, Any]:
	"""Внутренняя функция валидации сырых данных"""
	parsed_data = dict(urllib.parse.parse_qsl(raw_data, strict_parsing=True))

	if "hash" not in parsed_data:
		raise ValueError("Missing 'hash' field in init_data")

	received_hash = parsed_data.pop("hash")
	data_check_string = "\n".join(
		f"{k}={v}" for k, v in sorted(parsed_data.items())
	)

	# Проверка подписи
	secret_key = hmac.new(
		b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256
	).digest()
	computed_hash = hmac.new(
		secret_key, data_check_string.encode(), hashlib.sha256
	).hexdigest()

	if not hmac.compare_digest(received_hash, computed_hash):
		raise ValueError("Invalid init_data signature")

	# Парсим JSON поля
	for key in ["user", "chat"]:
		if key in parsed_data:
			parsed_data[key] = json.loads(parsed_data[key])

	# Проверка свежести
	auth_date = int(parsed_data.get("auth_date", 0))
	now = int(time.time())
	if now - auth_date > 3600:
		raise ExpiredTelegramDataError("init_data is too old (older than 1 hour)")

	parsed_data["hash"] = received_hash
	return parsed_data

def save_avatar(user, photo_url):
	if not photo_url or user.avatar_path:
		return

	with httpx.Client(follow_redirects=True) as client:
		try:
			# response = sync_http_client.get(url=photo_url, response_type="response", raise_for_status=True, follow_redirects=True)
			response = client.get(photo_url)
			response.raise_for_status()
		except httpx.HTTPStatusError as e:
			logger.warning(f"Telegram avatar download failed: {e}")
			return
		except httpx.RequestError as e:
			logger.warning(f"Telegram avatar request failed: {e}")
			return

	content_type = response.headers.get("Content-Type", "")
	if content_type == "image/svg+xml":
		return

	user.avatar_path.save(
		f"{user.telegram_id}.jpg",
		ContentFile(response.content),
		save=True
	)
