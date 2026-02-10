from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.models import Tournament, TournamentRegistration
from apps.tournaments.api.serializers import TournamentRegistrationSerializer

@extend_schema(
	tags=["Tournaments"],
	summary="Получить данные о доступных местах",
	responses={
		200: {
			"type": "object",
			"properties": {
				"available_registrations": {"type": "integer"},
				"available_waitlists": {"type": "integer"}
			}
		}
	}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def availability(request, pk):
	"""
	GET /api/tournaments/{id}/availability/
	"""
	tournament = Tournament.objects.filter(pk=pk).first()
	if not tournament:
		return Response({"detail": "Турнир не найден"}, status=404)

	available_registrations = max(tournament.max_participants - tournament.get_participants_count(), 0)
	available_waitlists = max(tournament.max_waitlist - tournament.get_waitlist_count(), 0)

	return Response({"registrations": available_registrations, "waitlists": available_waitlists})

@extend_schema(
	tags=["Tournaments"],
	summary="Проверить регистрацию в турнире",
	responses={
		200: {
			"type": "object",
			"properties": {
				"status": {
					"type": "string",
					"enum": TournamentRegistration.StatusType.values,
					"nullable": True
				},
			}
		},
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

	registration = TournamentRegistration.objects.filter(tournament=tournament, user=user).first()

	return Response({"status": registration.status if registration else None})

@extend_schema(
	tags=["Tournaments"],
	summary="Регистрация в турнире",
	responses={
		201: TournamentRegistrationSerializer,
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

		can, error = tournament.can_register(user)
		if not can:
			return Response({"detail": error}, status=400)

		status_type = tournament.compute_registration_status()
		if not status_type:
			return Response({"detail": "Достигнут лимит участников"}, status=400)

		registration = TournamentRegistration.objects.create(
			tournament=tournament,
			user=user,
			status=status_type
		)

	serializer = TournamentRegistrationSerializer(registration, context={"request": request})
	return Response(serializer.data, status=201)

@extend_schema(
	tags=["Tournaments"],
	summary="Отменить регистрацию в турнире",
	responses={
		204: None,
		400: {
			"type": "object",
			"properties": {
				"detail": {"type": "string"}
			}
		}
	}
)
@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def unregister(request, pk):
	"""
	DELETE /api/tournaments/{id}/unregister/
	"""
	user = request.user

	with transaction.atomic():
		tournament = Tournament.objects.select_for_update().filter(pk=pk).first()
		if not tournament:
			return Response({"detail": "Турнир не найден"}, status=404)

		if tournament.status != Tournament.StatusType.IN_QUEUE:
			return Response({"detail": "Регистрация закрыта"}, status=400)

		deleted_count, _ = TournamentRegistration.objects.filter(tournament=tournament, user=user).delete()

		if tournament.get_participants_count() < tournament.max_participants:
			waitlist_registration = TournamentRegistration.objects.filter(
				tournament=tournament,
				status=TournamentRegistration.StatusType.WAITLIST
			).order_by("created_at").first()

			if waitlist_registration:
				waitlist_registration.status = TournamentRegistration.StatusType.REGISTERED
				waitlist_registration.save()

	return Response(status=204)
