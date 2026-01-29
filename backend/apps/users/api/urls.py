from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="users")

app_name = "users"

urlpatterns = [
	path("auth/telegram/", views.TelegramAuthAPIView.as_view(), name="telegram-auth"),
	path("", include(router.urls)),
]
