import logging
import httpx

from celery_app import app
from celery_app.config import settings

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def tournament_lifecycle_task(self, method: str, tournament_id):
	"""
	Задача Celery для запуска турнира.
	Вызывает внутренний API бэкенда.
	"""
	logger.info(f"method: {method} | tournament_id: {tournament_id}")

	try:
		response = httpx.post(
			url=f'{settings.app.api_url}/tournaments/{tournament_id}/{method}-internal/',
			headers = {"X-Internal-Api-Key": settings.secret_key},
			timeout=10
		)

		if response.status_code == 400:
			logger.info(f"status_code 400: {response.text}")
			return

		response.raise_for_status()

	except httpx.HTTPStatusError as exc:
		if exc.response.status_code in [500, 502, 503, 504, 429]:
			logger.info(f"HTTPStatusError [{exc.response.status_code}]: {exc.response.text}")
			self.retry(exc=exc, countdown=60 * self.request.retries)  # Экспоненциальная backoff

	except Exception as exc:
		# Логируем неожиданные ошибки
		logger.error(f"Unexpected error starting tournament {tournament_id}: {exc}")
		raise
