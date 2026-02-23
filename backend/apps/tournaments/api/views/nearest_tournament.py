from datetime import timedelta
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.api.serializers import TournamentRegistrationSerializer, TournamentSerializer
from apps.tournaments.models import Tournament, TournamentRegistration

@extend_schema(
	tags=["Tournaments"],
	summary="Получить ближайший турнир",
	responses={200: TournamentSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def nearest(request):
	"""
	GET /api/tournaments/nearest/
	"""
	now = timezone.now()
	min_start_time = now + timedelta(minutes=30)

	tournament = (
		Tournament.objects
		.filter(status=Tournament.StatusType.IN_QUEUE, started_at__gte=min_start_time)
		.order_by("started_at")
		.first()
	)

	if not tournament:
		return Response({"detail": "Ближайший турнир не найден"}, status=404)

	serializer = TournamentSerializer(tournament, context={"request": request})
	return Response(serializer.data)

@extend_schema(
	tags=["Tournaments"],
	summary="Получить сегодняшний турнир",
	# responses={200: TournamentSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_status(request):
	"""
	GET /api/tournaments/today-status/
	"""
	now = timezone.localtime()

	today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
	today_end = today_start + timedelta(days=1)

	tournament = (
		Tournament.objects
		.filter(
			status__in=[Tournament.StatusType.IN_QUEUE, Tournament.StatusType.ACTIVE],
			started_at__gte=today_start,
			started_at__lt=today_end
		)
		.order_by("started_at") # берем который уже запустился (активный) либо тот который ближе к запуску
		.first()
	)

	if not tournament:
		return Response({"detail": "Сегодняшний турнир не найден"}, status=404)

	tournament_registration = TournamentRegistration.objects.filter(tournament=tournament, user=request.user).first()

	if not tournament_registration:
		return Response({"detail": "Пользователь не зарегистрирован в сегодняшнем турнире"}, status=404)

	return Response({"title": tournament.title, "status": tournament_registration.status})

