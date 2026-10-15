import hashlib
import hmac
import json
import time

import httpx


class NenadengiClient:
	def __init__(self, base_url: str, api_key: str, secret: str):
		self.base_url = base_url.rstrip("/")
		self.api_key = api_key
		self.secret = secret
		self._client = httpx.Client(timeout=15)

	def _sign(self, body: str) -> dict:
		ts = str(int(time.time()))
		signature = hmac.new(self.secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
		return {"X-Timestamp": ts, "X-Signature": signature}

	def _post(self, path: str, payload: dict, idempotency_key: str) -> httpx.Response:
		body = json.dumps(payload, ensure_ascii=False)
		headers = {
			"Content-Type": "application/json",
			"X-Api-Key": self.api_key,
			"Idempotency-Key": idempotency_key,
			**self._sign(body),
		}
		response = self._client.post(f"{self.base_url}{path}", content=body.encode(), headers=headers)
		response.raise_for_status()
		return response

	def upsert_event(self, payload: dict, idempotency_key: str) -> httpx.Response:
		return self._post("/events", payload, idempotency_key)

	def post_results(self, external_id: str, payload: dict, idempotency_key: str) -> httpx.Response:
		return self._post(f"/events/{external_id}/results", payload, idempotency_key)

	def post_occupancy(self, external_id: str, payload: dict, idempotency_key: str) -> httpx.Response:
		return self._post(f"/events/{external_id}/occupancy", payload, idempotency_key)

	def update_registration_status(self, registration_id: str, payload: dict, idempotency_key: str) -> httpx.Response:
		return self._post(f"/registrations/{registration_id}/status", payload, idempotency_key)
