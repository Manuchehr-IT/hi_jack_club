import httpx
from typing import List

from core.config import settings

class UserService:
	@staticmethod
	async def get_user_ids() -> List[int]:
		response = httpx.get(f"{settings.app.api_url}/users/", headers = {"X-Internal-Api-Key": settings.secret_key}, timeout=10)
		response.raise_for_status()

		results = response.json()

		return [res["telegram_id"] for res in results]
