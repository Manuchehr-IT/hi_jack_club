from django.conf import settings

from .client import IikoClient
from .local_client import IikoLocalClient
from .services import IikoService
from apps.redis import redis_client

def create_iiko_client() -> IikoClient:
	return IikoClient(base_url=settings.IIKO_BASE_URL, api_key=settings.IIKO_API_KEY, organization_id=settings.IIKO_ORGANIZATION_ID, redis_client=redis_client)

def create_iiko_local_client() -> IikoLocalClient:
	return IikoLocalClient(base_url=settings.IIKO_LOCAL_BASE_URL, login=settings.IIKO_LOCAL_LOGIN, password=settings.IIKO_LOCAL_PASSWORD, redis_client=redis_client)

def create_iiko_service() -> IikoService:
	return IikoService(
		iiko_client=create_iiko_client(),
		iiko_local_client=create_iiko_local_client(),
	)
