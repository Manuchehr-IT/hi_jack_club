from django.conf import settings

from .client import IikoClient

def create_iiko_client() -> IikoClient:
	return IikoClient(base_url=settings.IIKO_BASE_URL, api_key=settings.IIKO_API_KEY, organization_id=settings.IIKO_ORGANIZATION_ID)
