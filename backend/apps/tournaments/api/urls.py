from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import tournament_views, tournament_participants, tournament_registration, nearest_tournament, start_tournament

router = DefaultRouter()
router.register(r"", tournament_views.TournamentViewSet, basename="tournament")

app_name = "tournaments"

urlpatterns = [
	path("tournaments/", include([
		# Кастомные endpoints через @api_view
		path("nearest/", nearest_tournament.nearest),
		path("<int:pk>/registration-status/", tournament_registration.registration_status),
		path("<int:pk>/register/", tournament_registration.register),
		path("<int:pk>/unregister/", tournament_registration.unregister),
		path("<int:pk>/participants/", tournament_participants.participants),
		path("<int:pk>/start-internal/", start_tournament.start_internal),

		# Router.urls В САМОМ КОНЦЕ
		path("", include(router.urls)),
	]))
]