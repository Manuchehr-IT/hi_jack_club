from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.models import Tournament
from apps.tournaments.api.serializers import TournamentSerializer

@extend_schema(
	tags=["Tournaments"],
	summary="Получить ближайший турнир",
	responses={200: TournamentSerializer()}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def nearest(request):
	"""
	GET /api/tournaments/nearest/
	"""
	now = timezone.now()

	tournament = (
		Tournament.objects
		.filter(status=Tournament.StatusType.IN_QUEUE, started_at__gte=now)
		.order_by("started_at")
		.first()
	)

	if not tournament:
		return Response({"detail": "Ближайший турнир не найден"}, status=404)

	serializer = TournamentSerializer(tournament, context={"request": request})
	return Response(serializer.data)
