from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from apps.tournaments.api.serializers import TournamentSerializer
from apps.tournaments.models import Tournament

@extend_schema(tags=["Tournaments"])
class TournamentViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = TournamentSerializer
	permission_classes = [permissions.IsAuthenticated]
	queryset = Tournament.objects.all()

	def get_queryset(self):
		queryset = super().get_queryset()
		return queryset

	def list(self, request):
		status_param = request.query_params.get("status")
		queryset = self.get_queryset()

		if status_param:
			queryset = queryset.filter(status=status_param)

		queryset = queryset.order_by("started_at")

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)
