import httpx

class IikoClient:
	def __init__(self, base_url: str, api_key: str, organization_id: str):
		self.base_url = base_url
		self.api_key = api_key
		self.organization_id = organization_id

	def _get_access_token(self) -> str:
		url = f"{self.base_url}/access_token"
		params = {"apiLogin": self.api_key}

		response = httpx.post(url, json=params)
		response.raise_for_status()
		access_token = response.json()["token"]
		return access_token

	def _get_headers(self) -> dict:
		return {"Authorization": f"Bearer {self._get_access_token()}"}

	def get_customer_info(self, customer_id: str, type: str = "id") -> dict:
		url = f"{self.base_url}/loyalty/iiko/customer/info"
		params = {"customer_id": customer_id, "type": type, "organizationId": self.organization_id}

		response = httpx.post(url, headers=self._get_headers(), json=params)
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
		response = httpx.post(url, headers=self._get_headers(), json=params)
		response.raise_for_status()
		return response.json()
