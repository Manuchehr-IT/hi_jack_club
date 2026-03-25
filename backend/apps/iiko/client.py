import httpx
import logging
from redis import Redis

logger = logging.getLogger(__name__)

class IikoClient:
	ACCESS_TOKEN_KEY = "iiko:access_token"
	ACCESS_TOKEN_LOCK = "iiko:access_token:lock"
	ACCESS_TOKEN_TTL = 55 * 60  # 55 минут

	def __init__(self, base_url: str, api_key: str, organization_id: str, redis_client: Redis):
		self.base_url = base_url
		self.api_key = api_key
		self.organization_id = organization_id
		self.redis = redis_client
		self._client = httpx.Client(timeout=15)

	def _create_access_token(self) -> str:
		url = f"{self.base_url}/access_token"
		params = {"apiLogin": self.api_key}

		response = self._client.post(url, json=params)
		response.raise_for_status()
		return response.json()["token"]

	def _get_access_token(self) -> str:
		token = self.redis.get(self.ACCESS_TOKEN_KEY)
		if token:
			return token.decode("utf-8")

		with self.redis.lock(self.ACCESS_TOKEN_LOCK):
			token = self.redis.get(self.ACCESS_TOKEN_KEY)
			if token:
				return token.decode("utf-8")

			token = self._create_access_token()
			self.redis.set(self.ACCESS_TOKEN_KEY, token, ex=self.ACCESS_TOKEN_TTL)

			return token

	def _get_headers(self) -> dict:
		token = self._get_access_token()
		return {"Authorization": f"Bearer {token}"}

	def get_customer_info(self, customer_id: str, type: str = "id") -> dict:
		url = f"{self.base_url}/loyalty/iiko/customer/info"
		params = {type: customer_id, "type": type, "organizationId": self.organization_id}

		response = self._client.post(url, headers=self._get_headers(), json=params)
		response.raise_for_status()
		return response.json()

	def create_or_update_customer(self, phone: str, card: str, name: str) -> dict:
		url = f"{self.base_url}/loyalty/iiko/customer/create_or_update"
		params = {
			"organizationId": self.organization_id,
			"phone": phone,
			"cardTrack": card,
			"cardNumber": card,
			"name": name,
		}
		response = self._client.post(url, headers=self._get_headers(), json=params)
		response.raise_for_status()
		return response.json()
