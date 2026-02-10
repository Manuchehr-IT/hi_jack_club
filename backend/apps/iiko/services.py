import httpx

from apps.iiko.client import IikoClient

class IikoService:
	def __init__(self, iiko_client: IikoClient):
		self.iiko_client = iiko_client

	def create_or_update_user(self, phone: str, card: str, name: str) -> dict:
		return self.iiko_client.create_or_update_customer(phone, card, name)
