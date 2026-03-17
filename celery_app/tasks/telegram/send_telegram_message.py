import httpx
import logging
from celery import Task, group
from datetime import datetime
from typing import List

from .schemas import SendMethod
from celery_app import app

logger = logging.getLogger(__name__)

class TaskMonitor(Task):
	"""Базовый класс для мониторинга задач"""

	def on_success(self, retval, task_id, args, kwargs):
		logger.info(f"✅ Task {task_id} completed successfully")
		# Отправить метрику в Prometheus/StatsD
		# metrics.counter('task.success', tags={'name': self.name})

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.error(f"❌ Task {task_id} failed: {exc}")
		# metrics.counter('task.failure', tags={'name': self.name})

@app.task(bind=True, base=TaskMonitor, rate_limit="30/s", max_retries=3)
def send_telegram(self, telegram_bot_token: str, method: SendMethod, chat_id: int, **kwargs):
	"""Основная задача для отправки сообщений"""

	try:
		url = f"https://api.telegram.org/bot{telegram_bot_token}/{method}"
		payload = {"chat_id": chat_id, "parse_mode": "HTML", **kwargs}

		response = httpx.post(url, json=payload, timeout=10)
		response.raise_for_status()
		result = response.json()

		return result
	except Exception as exc:
		error_str = str(exc)

		soft_errors = [
			"bot was blocked by the user",
			"user is deactivated", 
			"chat not found",
			"user_is_blocked",
			"bots can’t send message to bots",
			"message is too long"
		]
		if any(phrase in error_str for phrase in soft_errors):
			logger.warning(f"⏭️ Permanent failure for {chat_id}: {error_str}")
			return

		raise self.retry(exc=exc, countdown=min(60 * (self.request.retries + 1), 300))

@app.task(bind=True)
def broadcast_messages(self, telegram_bot_token: str, method: SendMethod, chat_ids: List[int], **kwargs):
	"""
	Задача для массовой рассылки.
	Создает подзадачи для каждого пользователя.
	"""
	logger.info(f"Starting broadcast to {len(chat_ids)} users")

	BATCH_SIZE = 1000
	batches = [chat_ids[i:i + BATCH_SIZE] for i in range(0, len(chat_ids), BATCH_SIZE)]

	logger.info(f"Split into {len(batches)} batches of up to {BATCH_SIZE} users each")

	jobs = []
	for i, batch in enumerate(batches, 1):
		logger.info(f"Creating batch {i}/{len(batches)} with {len(batch)} users")

		job = group(
			send_telegram.s(
				telegram_bot_token=telegram_bot_token,
				method=method,
				chat_id=user_id,
				**kwargs,
			)
			for user_id in batch
		).apply_async()

		jobs.append({
			"batch_id": i,
			"group_id": job.id,
			"user_count": len(batch)
		})

	return {
		"broadcast_id": self.request.id,
		"batch_jobs": jobs,
		"total_users": len(chat_ids),
		"batches": len(batches),
		"started_at": datetime.now().isoformat()
	}

# @app.task(bind=True)
# def broadcast_completed(self, results, total):
# 	"""Callback после завершения рассылки"""
# 	successful = sum(1 for r in results if r and not isinstance(r, Exception))
# 	failed = total - successful

# 	logger.info(f"Broadcast completed. Success: {successful}, Failed: {failed}")

# 	return {
# 		"total": total,
# 		"successful": successful,
# 		"failed": failed,
# 		"completed_at": datetime.now().isoformat()
# 	}
