from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Tournament, TournamentRegistration
from .serializers import TournamentSerializer, TournamentRegistrationSerializer

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
