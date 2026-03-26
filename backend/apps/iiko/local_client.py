from datetime import date
import httpx
import logging
from redis import Redis

logger = logging.getLogger(__name__)

class IikoLocalClient:
	TOKEN_KEY = "iiko_local:token_key"
	TOKEN_KEY_LOCK = "iiko_local:token_key:lock"
	TOKEN_KEY_TTL = 55 * 60  # 55 минут

	def __init__(self, base_url: str, login: str, password: str, redis_client: Redis):
		self.base_url = base_url
		self.login = login
		self.password = password
		self.redis = redis_client
		self._client = httpx.Client(timeout=15)

	def _auth(self) -> str:
		url = f"{self.base_url}/auth"
		data = {"login": self.login, "pass": self.password}

		response = self._client.post(url, data=data)
		response.raise_for_status()
		return response.text

	def _get_token_key(self) -> str:
		token = self.redis.get(self.TOKEN_KEY)
		if token:
			return token.decode("utf-8")

		with self.redis.lock(self.TOKEN_KEY_LOCK):
			token = self.redis.get(self.TOKEN_KEY)
			if token:
				return token.decode("utf-8")

			token = self._auth()
			self.redis.set(self.TOKEN_KEY, token, ex=self.TOKEN_KEY_TTL)

			return token

	def _get_params(self) -> dict:
		key = self._get_token_key()
		return {"key": key}

	def get_olap_report(self, from_date: date, to_date: date, **filters) -> dict:
		url = f"{self.base_url}/v2/reports/olap"
		data = {
			"reportType": "SALES",
			"groupByRowFields": [
				"Delivery.CustomerName",
				"OrderNum",
				# "Delivery.CustomerPhone",
				"Delivery.CustomerCardNumber",
				# "DishId",
				"OpenTime",
				"CloseTime",
				"DishName",
				"DishServicePrintTime"
			],
			"groupByColFields": [],
			"aggregateFields": [
				"DishAmountInt",
				"sumAfterDiscountWithoutVAT",
			],
			"filters": {
				"OpenDate.Typed": {
					"filterType": "DateRange",
					"from": from_date.isoformat(),
					"to": to_date.isoformat(),
					"includeLow": True,
					"includeHigh": False
				},
				"DeletedWithWriteoff": {
					"filterType": "IncludeValues",
					"values": ["NOT_DELETED"]
				},
				"OrderDeleted": {
					"filterType": "IncludeValues",
					"values": ["NOT_DELETED"]
				},
				**filters
			}
		}

		response = self._client.post(url, params=self._get_params(), json=data)
		response.raise_for_status()
		return response.json()
