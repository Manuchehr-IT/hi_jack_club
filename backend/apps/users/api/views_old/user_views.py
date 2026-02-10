from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.iiko.factory import create_iiko_client
from apps.users.api.serializers import UserSerializer, UpdateProfileSerializer
from apps.users.factory import create_user_service
from apps.users.utils import create_qr

User = get_user_model()

@extend_schema(tags=["Users"])
class UserViewSet(ListModelMixin, GenericViewSet):
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticated]
	queryset = User.objects.all()
	filter_backends = [filters.OrderingFilter]
	ordering_fields = ["created_at", "knockouts", "rating"]
	ordering = ["created_at"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user_service = create_user_service()
		self.iiko_client = create_iiko_client()

	def get_queryset(self):
		queryset = super().get_queryset()
		limit = self.request.query_params.get("limit")
		if limit and limit.isdigit():
			queryset = queryset[:int(limit)]
		return queryset

	@extend_schema(
		request=UpdateProfileSerializer,
		responses=UserSerializer,
	)
	@action(detail=False, methods=["patch"])
	def sign_up(self, request):
		if request.user.privacy_policy_accepted:
			return Response(UserSerializer(request.user).data)

		serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True, context={"request": request}, is_signup=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		validated = serializer.validated_data
		full_phone = validated["phone_code"] + validated["phone"]

		iiko_data = self.iiko_client.create_or_update_customer(phone=full_phone, card=validated["phone"], name=request.user.first_name)
		customer_id = iiko_data.get("id")
		if customer_id:
			request.user.iiko_id = customer_id
			request.user.save()
			create_qr(request.user, validated["phone"])

		return Response(UserSerializer(request.user).data)
