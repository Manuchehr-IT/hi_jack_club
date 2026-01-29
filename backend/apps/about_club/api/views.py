from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ..models import AboutClub
from .serializers import AboutClubSerializer

@extend_schema(tags=["AboutClub"])
class AboutClubViewSet(ListModelMixin, GenericViewSet):
	serializer_class = AboutClubSerializer
	permission_classes = [AllowAny]
	queryset = AboutClub.objects.all()
	ordering = ["sort_order", "id"]

	def get_queryset(self):
		queryset = super().get_queryset()
		queryset = queryset.filter(is_active=True)
		limit = self.request.query_params.get("limit")
		if limit and limit.isdigit():
			queryset = queryset[:int(limit)]
		return queryset
