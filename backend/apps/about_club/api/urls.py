from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"about_club", views.AboutClubViewSet, basename="about_club")

app_name = "about_club"

urlpatterns = [
    path("", include(router.urls)),
]