from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"tournaments", views.TournamentViewSet, basename="tournament")

app_name = "tournaments"

urlpatterns = [
    path("", include(router.urls)),
]