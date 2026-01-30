import logging
from datetime import datetime
from typing import List

from celery_app import app

logger = logging.getLogger(__name__)

@app.task(bind=True, rate_limit="30/s", max_retries=3) # ignore_result=True
def send_message(self, telegram_bot_token: str, chat_id: int, text: str, **kwargs):
	"""Основная задача для отправки сообщений"""
	print("SENDING MESSAGE")
	from .client import TelegramAPIClient

	try:
		client = TelegramAPIClient(token=telegram_bot_token)
		result = client.send_message(chat_id, text, **kwargs)

		logger.info(f"Sent to {chat_id}: {text[:50]}...")
		return result
	except Exception as exc:
		logger.error(f"Failed to send to {chat_id}: {exc}")

		error_str = str(exc)

		soft_errors = [
			"bot was blocked by the user",
			"user is deactivated", 
			"chat not found",
			"user_is_blocked",
		]
		if any(phrase in error_str for phrase in soft_errors):
			logger.warning(f"Permanent failure for {chat_id}: {error_str}")
			return

		raise self.retry(exc=exc, countdown=min(60 * self.request.retries, 300))

@app.task(bind=True)
def broadcast_messages(self, user_ids: List[int], text: str, **kwargs):
	"""
	Задача для массовой рассылки.
	Создает подзадачи для каждого пользователя.
	"""
	logger.info(f"Starting broadcast to {len(user_ids)} users")

	task_ids = []
	for user_id in user_ids:
		task = send_message.delay(
			chat_id=user_id,
			text=text,
			**kwargs,
		)
		task_ids.append(task.id)

	return {
		"broadcast_id": self.request.id,
		"total_users": len(user_ids),
		"task_ids": task_ids,
		"started_at": datetime.now().isoformat()
	}