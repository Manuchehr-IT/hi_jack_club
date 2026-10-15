from django.conf import settings

from .client import NenadengiClient


def create_nenadengi_client() -> NenadengiClient:
	return NenadengiClient(
		base_url=settings.NENADENGI_BASE_URL,
		api_key=settings.NENADENGI_API_KEY,
		secret=settings.NENADENGI_SECRET,
	)
