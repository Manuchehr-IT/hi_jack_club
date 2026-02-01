import logging
import httpx

from celery_app import app
from celery_app.config import settings

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def start_tournament_task(self, tournament_id):
	"""
	Задача Celery для запуска турнира.
	Вызывает внутренний API бэкенда.
	"""
	try:
		response = httpx.post(
			url=f'{settings.app.api_url}/tournaments/{tournament_id}/start-internal/',
			headers = {"X-Internal-Api-Key": settings.secret_key},
			timeout=10
		)

		if response.status_code == 400:
			pass

		response.raise_for_status()

	except httpx.HTTPStatusError as exc:
		if exc.response.status_code in [500, 502, 503, 504, 429]:
			self.retry(exc=exc, countdown=60 * self.request.retries)  # Экспоненциальная backoff

	except Exception as exc:
		# Логируем неожиданные ошибки
		logger.error(f"Unexpected error starting tournament {tournament_id}: {exc}")
		raise