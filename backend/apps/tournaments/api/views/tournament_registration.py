from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.models import Tournament, TournamentRegistration
from apps.tournaments.api.serializers import TournamentRegistrationSerializer

@extend_schema(
	tags=["Tournaments"],
	summary="Проверить регистрацию в турнире",
	responses={
		200: {
			"type": "object",
			"properties": {
				"is_registered": {"type": "boolean"},
			}
		},
		404: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def registration_status(request, pk):
	"""
	GET /api/tournaments/{id}/registration-status/
	"""
	user = request.user
	tournament = Tournament.objects.filter(pk=pk).first()
	if not tournament:
		return Response({"detail": "Турнир не найден"}, status=404)

	is_registered = TournamentRegistration.objects.filter(tournament=tournament, user=user).exists()

	return Response({"is_registered": is_registered})

@extend_schema(
	tags=["Tournaments"],
	summary="Регистрация в турнире",
	responses={
		201: TournamentRegistrationSerializer(),
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request, pk):
	"""
	POST /api/tournaments/{id}/register/
	"""
	user = request.user

	with transaction.atomic():
		tournament = Tournament.objects.select_for_update().filter(pk=pk).first()
		if not tournament:
			return Response({"detail": "Турнир не найден"}, status=404)

		if tournament.get_participants_count() >= tournament.max_participants:
			# TODO: Сделать запрос в waitlist если есть места.
			return Response({"detail": "Достигнут лимит участников"}, status=400)

		if tournament.status != Tournament.StatusType.IN_QUEUE:
			return Response({"detail": "Регистрация на этот турнир закрыта"}, status=400)

		registration, created = TournamentRegistration.objects.get_or_create(tournament=tournament, user=user)

		if not created:
			return Response({"detail": "Вы уже зарегистрированы на этот турнир"}, status=400)

	serializer = TournamentRegistrationSerializer(registration, context={"request": request})
	return Response(serializer.data, status=201)

@extend_schema(
	tags=["Tournaments"],
	summary="Отменить регистрацию в турнире",
	responses={204: None}
)
@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def unregister(request, pk):
	"""
	DELETE /api/tournaments/{id}/unregister/
	"""
	user = request.user
	tournament = Tournament.objects.filter(pk=pk).first()
	if not tournament:
		return Response({"detail": "Турнир не найден"}, status=404)

	deleted_count, _ = TournamentRegistration.objects.filter(tournament=tournament, user=user).delete()

	return Response(status=204)
