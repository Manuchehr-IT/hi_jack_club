from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ..models import SocialNetwork
from .serializers import SocialNetworkSerializer

@extend_schema(tags=["SocialNetwork"])
class SocialNetworkViewSet(ListModelMixin, GenericViewSet):
    serializer_class = SocialNetworkSerializer
    permission_classes = [AllowAny]
    queryset = SocialNetwork.objects.all()
    ordering = ["id"]

    @extend_schema(description="Получить ссылки в виде словаря {тип: ссылка}")
    @action(detail=False, methods=['get'])
    def as_dict(self, request):
        links = self.get_queryset()

        data = {}
        for link in links:
            data[link.social_type] = link.url or ''

        return Response(data)

    def get_queryset(self):
        return SocialNetwork.objects.all()
