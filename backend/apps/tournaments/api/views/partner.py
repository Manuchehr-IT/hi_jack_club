from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.tournaments.models import Tournament

class PartnerApiPermission(permissions.BasePermission):
	"""Проверка ключа для внешних сервисов-партнёров.

	Специально отдельный от X-Internal-Api-Key/SECRET_KEY: тот ключ используется
	для подписи JWT и не должен передаваться сторонним сервисам.
	"""

	def has_permission(self, request, view):
		if request.method == "OPTIONS":
			return True

		if not settings.PARTNER_API_KEY:
			return False

		api_key = request.headers.get("X-Partner-Api-Key")
		if not api_key:
			return False
		return api_key == settings.PARTNER_API_KEY

@extend_schema(
	tags=["Partner API"],
	summary="Список турниров для внешних партнёрских сервисов",
	description="Только для вызова с правильным X-Partner-Api-Key. По умолчанию отдаёт турниры в статусе IN_QUEUE.",
	responses={
		200: {
			"type": "array",
			"items": {
				"type": "object",
				"properties": {
					"id": {"type": "integer"},
					"title": {"type": "string"},
					"location": {"type": "string"},
					"started_at": {"type": "string", "format": "date-time"},
					"status": {"type": "string"},
					"icon": {"type": "string", "format": "uri", "nullable": True}
				}
			}
		}
	}
)
@api_view(["GET"])
@permission_classes([PartnerApiPermission])
def list_tournaments(request):
	"""
	GET /api/tournaments/partner/tournaments/?status=IN_QUEUE
	"""
	status_param = request.query_params.get("status") or Tournament.StatusType.IN_QUEUE
	queryset = Tournament.objects.filter(status=status_param).order_by("started_at")

	return Response([
		{
			"id": tournament.id,
			"title": tournament.title,
			"location": tournament.location,
			"started_at": tournament.started_at.isoformat(),
			"status": tournament.status,
			"icon": request.build_absolute_uri(tournament.icon.url) if tournament.icon else None,
		}
		for tournament in queryset
	])
