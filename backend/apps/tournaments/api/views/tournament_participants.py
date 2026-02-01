from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tournaments.api.serializers import TournamentRegistrationSerializer
from apps.tournaments.models import Tournament, TournamentRegistration

@extend_schema(
	tags=["Tournaments"],
	summary="Получить участников турнира",
	responses={200: TournamentRegistrationSerializer()}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def participants(request, pk):
	"""
	GET /api/tournaments/{id}/participants/
	"""
	tournament = get_object_or_404(Tournament, pk=pk)

	participants = TournamentRegistration.objects.filter(tournament=tournament, status=TournamentRegistration.StatusType.REGISTERED).select_related("user")

	serializer = TournamentRegistrationSerializer(participants, many=True, context={"request": request})
	return Response(serializer.data)
