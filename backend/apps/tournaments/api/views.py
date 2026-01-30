from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Tournament, TournamentRegistration
from .serializers import TournamentSerializer, TournamentRegistrationSerializer

class InternalApiPermission(permissions.BasePermission):
	"""Проверка секретного ключа для внутренних API"""

	def has_permission(self, request, view):
		if request.method == 'OPTIONS':
			return True

		secret_key = request.headers.get('X-Internal-Api-Key')
		if not secret_key:
			return False
		return secret_key == settings.SECRET_KEY

@extend_schema(tags=["Tournaments"])
class TournamentViewSet(viewsets.ModelViewSet):
	serializer_class = TournamentSerializer
	permission_classes = [permissions.AllowAny]
	# permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Tournament.objects.all()

	@extend_schema(
		summary="Получить участников турнира",
		responses={
			200: TournamentRegistrationSerializer(many=True),
			201: TournamentRegistrationSerializer(many=True)
		}
	)
	@action(detail=True, methods=["get"], url_path="participants")
	def participants(self, request, pk=None):
		tournament = self.get_object()

		participants = TournamentRegistration.objects.filter(
			tournament=tournament,
			status=TournamentRegistration.StatusType.REGISTERED
		).select_related("user")

		serializer = TournamentRegistrationSerializer(participants, many=True)
		return Response(serializer.data, status=200)

	@extend_schema(
		summary="Проверить регистрацию в турнире",
		request=None,
		responses={
			200: {
				"type": "object",
				"properties": {
					"is_registered": {"type": "boolean"}
				}
			}
		}
	)
	@action(detail=True, methods=["get"], url_path="registration-status")
	def registration_status(self, request, pk=None):
		tournament = self.get_object()
		user = request.user

		is_registered = TournamentRegistration.objects.filter(tournament=tournament, user=user).exists()

		return Response({"is_registered": is_registered}, status=200)

	@extend_schema(
		summary="Регистрация в турнире",
		request=None,
		responses={201: TournamentRegistrationSerializer()}
	)
	@action(detail=True, methods=["post"], url_path="register")
	def register(self, request, pk=None):
		tournament = self.get_object()
		user = request.user

		registration, created = TournamentRegistration.objects.get_or_create(tournament=tournament, user=user)

		serializer = TournamentRegistrationSerializer(registration)
		return Response(serializer.data, status=201 if created else 200)

	@extend_schema(
		summary="Отменить регистрацию в турнире",
		request=None,
		responses={204: None}
	)
	@action(detail=True, methods=["delete"], url_path="unregister")
	def unregister(self, request, pk=None):
		tournament = self.get_object()
		user = request.user

		deleted, _ = TournamentRegistration.objects.filter(tournament=tournament, user=user).delete()

		return Response(status=204)

	@extend_schema(
		summary="Запустить турнир (внутренний API для Celery)",
		description="Используется Celery worker для автоматического старта турнира",
		request=None,
		responses={
			200: {
				"type": "object",
				"properties": {
					"status": {"type": "string", "example": "ACTIVE"},
					"id": {"type": "integer"},
					"started_at": {"type": "string", "format": "date-time"}
				}
			},
			400: {
				"type": "object",
				"properties": {
					"error": {"type": "string"},
					"started_at": {"type": "string", "format": "date-time"}
				}
			}
		},
		auth=None  # Указываем Swagger, что endpoint не требует стандартной аутентификации
	)
	@action(detail=True, methods=["post"], url_path="start-internal", permission_classes=[InternalApiPermission])
	def start_internal(self, request, pk=None):
		"""
		Внутренний endpoint для запуска турнира.
		Только для вызова из Celery worker с правильным X-Internal-Api-Key
		"""
		try:
			with transaction.atomic():
				tournament = Tournament.objects.select_for_update().get(id=pk)

				if tournament.status != Tournament.StatusType.IN_QUEUE:
					return Response(status=204)

				if tournament.started_at > timezone.now():
					return Response({
						"error": f"Tournament start time not reached yet: {tournament.started_at}",
						"started_at": tournament.started_at.isoformat()
					}, status=400)

				tournament.status = Tournament.StatusType.ACTIVE
				tournament.save()

				return Response({
					"status": "ACTIVE",
					"id": tournament.id,
					"started_at": tournament.started_at.isoformat()
				}, status=200)

		except Tournament.DoesNotExist:
			return Response({"error": f"Tournament with id {pk} not found"}, status=404)
		except Exception as e:
			return Response({"error": str(e)}, status=500)
