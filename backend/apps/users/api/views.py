from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UpdateProfileSerializer, TelegramAuthSerializer, AuthResponseSerializer
from ..factory import create_user_service
from ..utils import create_qr
from apps.iiko.factory import create_iiko_service

User = get_user_model()

class TelegramAuthAPIView(APIView):
	permission_classes = [AllowAny]
	authentication_classes = []

	def __init__(self):
		self.user_service = create_user_service()

	@extend_schema(
		request=TelegramAuthSerializer,
		responses={200: AuthResponseSerializer},
		description="Авторизация через Telegram Web App",
		tags=["Authentication"]
	)
	def post(self, request):
		"""
		Аутентификация через Telegram Web App
		"""
		serializer = TelegramAuthSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		tg_data = serializer.validated_data["init_data"]

		user, created = self.user_service.get_or_create_from_telegram(tg_data.user, tg_data.start_param)

		refresh_token = RefreshToken.for_user(user)

		return Response({
			"refresh": str(refresh_token),
			"access": str(refresh_token.access_token),
			"user": UserSerializer(user).data,
			"is_new_user": created
		})

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
		self.iiko_service = create_iiko_service()

	def get_queryset(self):
		queryset = super().get_queryset()
		limit = self.request.query_params.get("limit")
		if limit and limit.isdigit():
			queryset = queryset[:int(limit)]
		return queryset

	@action(detail=False, methods=["get"])
	def me(self, request):
		serializer = UserSerializer(request.user)
		return Response(serializer.data)

	@extend_schema(
		request=UpdateProfileSerializer,
		responses=UserSerializer,
	)
	@action(detail=False, methods=["patch"])
	def update_profile(self, request):
		serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(UserSerializer(request.user).data)

	@extend_schema(
		request=UpdateProfileSerializer,
		responses=UserSerializer,
	)
	@action(detail=False, methods=["patch"])
	def sign_up(self, request):
		if request.user.privacy_policy_accepted:
			return Response(UserSerializer(request.user).data)

		serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True, context={"is_signup": True})
		serializer.is_valid(raise_exception=True)
		serializer.save(privacy_policy_accepted=True)

		validated = serializer.validated_data
		full_phone = validated["phone"]
		phone_number = full_phone.lstrip(validated["phone_code"])

		iiko_data = self.iiko_service.create_or_update_user(phone=full_phone, card=phone_number, name=request.user.first_name)
		customer_id = iiko_data.get("id")
		if customer_id:
			request.user.iiko_id = customer_id
			request.user.save()
			create_qr(request.user, phone_number)

		return Response(UserSerializer(request.user).data)
