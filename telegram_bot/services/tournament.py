import httpx
from typing import Any, Dict, List

from core.config import settings

class TournamentService:
	@staticmethod
	async def get_in_queue_tournaments() -> List[Dict[str, Any]]:
		response = httpx.get(
			f"{settings.app.api_url}/tournaments/list-internal/",
			params={"status": "IN_QUEUE"},
			headers={"X-Internal-Api-Key": settings.secret_key},
			timeout=10
		)
		response.raise_for_status()

		return response.json()

	@staticmethod
	async def register(tournament_id: int, telegram_id: int) -> httpx.Response:
		return httpx.post(
			f"{settings.app.api_url}/tournaments/{tournament_id}/register-internal/",
			json={"telegram_id": telegram_id},
			headers={"X-Internal-Api-Key": settings.secret_key},
			timeout=10
		)

	@staticmethod
	async def unregister(tournament_id: int, telegram_id: int) -> httpx.Response:
		return httpx.post(
			f"{settings.app.api_url}/tournaments/{tournament_id}/unregister-internal/",
			json={"telegram_id": telegram_id},
			headers={"X-Internal-Api-Key": settings.secret_key},
			timeout=10
		)
