import logging
import httpx

from celery_app import app
from celery_app.config import settings

logger = logging.getLogger(__name__)

def _call_internal(path: str):
	response = httpx.post(
		url=f"{settings.app.api_url}{path}",
		headers={"X-Internal-Api-Key": settings.secret_key},
		timeout=20
	)
	response.raise_for_status()

_RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_event_task(self, tournament_id):
	"""Отправляет афишу турнира в nenadengi."""
	try:
		_call_internal(f"/tournaments/{tournament_id}/nenadengi-sync-event-internal/")
	except httpx.HTTPStatusError as exc:
		logger.warning(f"Nenadengi sync_event failed for tournament {tournament_id}: {exc.response.text}")
		if exc.response.status_code in _RETRYABLE_STATUS_CODES:
			self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
	except Exception as exc:
		logger.error(f"Unexpected error syncing event for tournament {tournament_id}: {exc}")
		raise

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_results_task(self, tournament_id):
	"""Отправляет итоговый ростер турнира в nenadengi."""
	try:
		_call_internal(f"/tournaments/{tournament_id}/nenadengi-sync-results-internal/")
	except httpx.HTTPStatusError as exc:
		logger.warning(f"Nenadengi sync_results failed for tournament {tournament_id}: {exc.response.text}")
		if exc.response.status_code in _RETRYABLE_STATUS_CODES:
			self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
	except Exception as exc:
		logger.error(f"Unexpected error syncing results for tournament {tournament_id}: {exc}")
		raise
