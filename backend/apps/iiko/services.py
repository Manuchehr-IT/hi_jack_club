import httpx

from apps.core.exceptions import CustomValidationError
from apps.iiko.client import IikoClient

class IikoService:
	def __init__(self, iiko_client: IikoClient):
		self.iiko_client = iiko_client

	def create_or_update_user(self, phone: str, card: str, name: str) -> dict:
		return self.iiko_client.create_or_update_customer(phone, card, name)

	def get_user_info_by_phone(self, phone: str) -> dict | None:
		try:
			return self.iiko_client.get_customer_info(customer_id=phone, type="phone")
		except httpx.HTTPStatusError as err:
			if err.response.status_code == 400:
				if err.response.headers.get("code") == "Transport_WrongCustomerNumber":
					return None
					# raise CustomValidationError(
					# 	code="iiko_customer_not_found",
					# 	message=f"Customer by phone '{phone}' not found",
					# 	status_code=404,
					# 	phone=phone
					# )
			raise err
