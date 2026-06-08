import logging
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UpdateProfileSerializer, TelegramAuthSerializer, AuthResponseSerializer
from ..factory import create_user_service
from ..utils import create_qr
from apps.core.exceptions import CustomValidationError
from apps.iiko.factory import create_iiko_service

User = get_user_model()

logger = logging.getLogger()

class TelegramAuthAPIView(APIView):
	permission_classes = [permissions.AllowAny]
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
		logger.info(f"TOKEN [{user.id}]: {refresh_token}")

		return Response({
			# "refresh": str(refresh_token),
			"access": str(refresh_token.access_token),
			"user": UserSerializer(user).data,
			"is_new_user": created
		})


class IsAuthenticatedOrInternalApi(permissions.BasePermission):
	"""Проверка секретного ключа для внутренних API"""

	def has_permission(self, request, view):
		if request.method == "OPTIONS":
			return True

		secret_key = request.headers.get("X-Internal-Api-Key")
		if secret_key and secret_key == settings.SECRET_KEY:
			return True

		return request.user and request.user.is_authenticated


@extend_schema(tags=["Users"])
class UserViewSet(ListModelMixin, GenericViewSet):
	serializer_class = UserSerializer
	permission_classes = [IsAuthenticatedOrInternalApi]
	pagination_class = LimitOffsetPagination
	queryset = User.objects.all()
	filter_backends = [filters.OrderingFilter]
	ordering_fields = ["created_at", "knockouts", "rating"]
	ordering = ["created_at"]

	def get_queryset(self):
		from django.db.models import Count, Q
		return User.objects.annotate(
			tournaments_count=Count('tournament_registrations', distinct=True)
		)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user_service = create_user_service()
		self.iiko_service = create_iiko_service()

	# def get_queryset(self):
	# 	queryset = super().get_queryset()
	# 	return queryset

	@action(detail=False, methods=["get"])
	def me(self, request):
		serializer = self.get_serializer(request.user)
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
		responses={
			200: UserSerializer,
			409: {
				"type": "object",
				"properties": {
					"code": {"type": "string"},
					"message": {"type": "string"},
					"field": {"type": "string"},
					"conflict_with": {"type": "string"},
				}
			}
		}
	)
	@action(detail=False, methods=["patch"])
	def sign_up(self, request):
		if request.user.privacy_policy_accepted:
			return Response(UserSerializer(request.user).data)

		serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True, context={"request": request, "is_signup": True})
		serializer.is_valid(raise_exception=True)

		validated = serializer.validated_data
		nickname = validated["nickname"]
		full_phone = validated["phone"]
		phone_number = full_phone.lstrip(validated["phone_code"])

		try:
			iiko_user = self.iiko_service.get_user_info_by_phone(phone=full_phone)
			if iiko_user:
				raise CustomValidationError(
					code="iiko_user_already_exists",
					message="A user with this number already exists in iiko",
					status_code=409,
					field="phone",
					conflict_with="existing_iiko_user",
				)

			iiko_data = self.iiko_service.create_or_update_user(phone=full_phone, card=phone_number, name=request.user.first_name)
			customer_id = iiko_data.get("id")
			if customer_id:
				request.user.iiko_id = customer_id
				request.user.save()
				create_qr(request.user, phone_number)
		except Exception as err:
			logger.error("Iiko [sign_up]", exc_info=err)
			raise CustomValidationError(
				code="iiko_api_error",
				message="Iiko API service error",
				status_code=503,
				original_error=str(err)
			)

		serializer.save(privacy_policy_accepted=True)

		return Response(UserSerializer(request.user).data)

	@action(detail=False, methods=["get"], url_path="monthly_rating")
	def monthly_rating(self, request):
		from django.db.models import Sum, Count, Q
		from django.utils import timezone
		from apps.tournaments.models import TournamentRegistration

		month_str = request.query_params.get("month")
		if month_str:
			try:
				year, month = map(int, month_str.split("-"))
			except (ValueError, AttributeError):
				return Response({"detail": "Неверный формат месяца. Используйте YYYY-MM."}, status=400)
		else:
			now = timezone.now()
			year, month = now.year, now.month

		results = (
			TournamentRegistration.objects
			.filter(
				tournament__started_at__year=year,
				tournament__started_at__month=month,
			)
			.exclude(points=0, knockouts=0)
			.values("user_id")
			.annotate(
				total_points=Sum("points"),
				total_knockouts=Sum("knockouts"),
				tournaments_count=Count("id"),
			)
			.order_by("-total_points")
		)

		user_ids = [r["user_id"] for r in results]
		users_map = {u.id: u for u in User.objects.filter(id__in=user_ids)}

		data = []
		for r in results:
			user = users_map.get(r["user_id"])
			if not user:
				continue
			avatar_url = None
			if user.avatar_path:
				avatar_url = request.build_absolute_uri(user.avatar_path.url)
			data.append({
				"id": user.id,
				"nickname": user.nickname,
				"username": user.username,
				"avatar_path": avatar_url,
				"rating": r["total_points"] or 0,
				"knockouts": r["total_knockouts"] or 0,
				"tournaments_count": r["tournaments_count"] or 0,
			})

		return Response(data)
