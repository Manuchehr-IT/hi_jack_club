from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializers import UserSerializer, TelegramAuthSerializer, AuthResponseSerializer
from apps.users.factory import create_user_service

class UserAuthAPIView(APIView):
	permission_classes = [AllowAny]
	authentication_classes = []

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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
