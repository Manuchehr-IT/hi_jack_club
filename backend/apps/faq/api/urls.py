from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"faq", views.FAQViewSet, basename="faq")

app_name = "faq"

urlpatterns = [
    path("", include(router.urls)),
]