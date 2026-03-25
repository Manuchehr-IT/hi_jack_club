from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.tournaments.models import Tournament

class InternalApiPermission(permissions.BasePermission):
	"""Проверка секретного ключа для внутренних API"""

	def has_permission(self, request, view):
		if request.method == "OPTIONS":
			return True

		secret_key = request.headers.get("X-Internal-Api-Key")
		if not secret_key:
			return False
		return secret_key == settings.SECRET_KEY

@extend_schema(
	tags=["Tournaments"],
	summary="Внутренний endpoint для запуска турнира.",
	description="Только для вызова из Celery worker с правильным X-Internal-Api-Key",
	responses={
		200: {
			"type": "object",
			"properties": {
				"id": {"type": "integer"},
				"status": {"type": "string", "example": "ACTIVE"},
				"started_at": {"type": "string", "format": "date-time"}
			}
		},
		400: {
			"type": "object",
			"properties": {
				"error": {"type": "string"},
				"started_at": {"type": "string", "format": "date-time"},
				"current_time": {"type": "string", "format": "date-time"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def start_internal(request, pk):
	"""
	POST /api/tournaments/{id}/start-internal
	"""
	try:
		with transaction.atomic():
			tournament = Tournament.objects.select_for_update().get(id=pk)
			current_time = timezone.now()

			if tournament.status != Tournament.StatusType.IN_QUEUE:
				return Response(
					{
						"error": "Tournament status is not IN_QUEUE",
						"started_at": tournament.started_at.isoformat(),
						"current_time": current_time
					},
					status=400
				)

			if tournament.started_at > timezone.now():
				return Response(
					{
						"error": f"Tournament start time not reached yet: {tournament.started_at}",
						"started_at": tournament.started_at.isoformat(),
						"current_time": current_time
					},
					status=400
				)

			tournament.status = Tournament.StatusType.ACTIVE
			tournament.save()

			return Response(
				{
					"id": tournament.id,
					"status": "ACTIVE",
					"started_at": tournament.started_at.isoformat()
				},
				status=200
			)

	except Tournament.DoesNotExist:
		return Response({"error": f"Tournament with id {pk} not found"}, status=404)
	except Exception as e:
		return Response({"error": str(e)}, status=500)

@extend_schema(
	tags=["Tournaments"],
	summary="Внутренний endpoint для завершения турнира.",
	description="Только для вызова из Celery worker с правильным X-Internal-Api-Key",
	responses={
		200: {
			"type": "object",
			"properties": {
				"id": {"type": "integer"},
				"status": {"type": "string", "example": "ACTIVE"},
				"started_at": {"type": "string", "format": "date-time"},
				"expires_at": {"type": "string", "format": "date-time"}
			}
		},
		400: {
			"type": "object",
			"properties": {
				"error": {"type": "string"},
				"started_at": {"type": "string", "format": "date-time"},
				"expires_at": {"type": "string", "format": "date-time"},
				"current_time": {"type": "string", "format": "date-time"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def finish_internal(request, pk):
	"""
	POST /api/tournaments/{id}/finish-internal
	"""
	try:
		with transaction.atomic():
			tournament = Tournament.objects.select_for_update().get(id=pk)
			# expires_at = tournament.started_at + timedelta(hours=9)
			expires_at = tournament.started_at + timedelta(minutes=2)
			current_time = timezone.now()

			if tournament.status != Tournament.StatusType.ACTIVE:
				return Response(
					{
						"error": "Tournament status is not ACTIVE",
						"started_at": tournament.started_at.isoformat(),
						"expires_at": expires_at.isoformat(),
						"current_time": current_time
					},
					status=400
				)

			if expires_at > current_time:
				return Response(
					{
						"error": f"Tournament finish time not reached yet: {expires_at}",
						"started_at": tournament.started_at.isoformat(),
						"expires_at": expires_at.isoformat(),
						"current_time": current_time
					},
					status=400
				)

			tournament.status = Tournament.StatusType.INACTIVE
			tournament.save()

			return Response(
				{
					"id": tournament.id,
					"status": "INACTIVE",
					"started_at": tournament.started_at.isoformat(),
					"expires_at": expires_at.isoformat()
				},
				status=200
			)

	except Tournament.DoesNotExist:
		return Response({"error": f"Tournament with id {pk} not found"}, status=404)
	except Exception as e:
		return Response({"error": str(e)}, status=500)
