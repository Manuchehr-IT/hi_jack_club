from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import tournament_views, tournament_participants, tournament_registration, nearest_tournament, tournament_lifecycle, partner, nenadengi_sync, nenadengi_webhook

router = DefaultRouter()
router.register(r"", tournament_views.TournamentViewSet, basename="tournament")

app_name = "tournaments"

urlpatterns = [
	path("tournaments/", include([
		path("nearest/", nearest_tournament.nearest),
		path("today-status/", nearest_tournament.today_status),
		path("<int:pk>/registration-status/", tournament_registration.registration_status),
		path("<int:pk>/register/", tournament_registration.register),
		path("<int:pk>/register-internal/", tournament_registration.register_internal),
		path("<int:pk>/unregister/", tournament_registration.unregister),
		path("<int:pk>/unregister-internal/", tournament_registration.unregister_internal),
		path("<int:pk>/availability/", tournament_registration.availability),
		path("<int:pk>/participants/", tournament_participants.participants),
		path("list-internal/", tournament_lifecycle.list_internal),
		path("partner/tournaments/", partner.list_tournaments),
		path("<int:pk>/start-internal/", tournament_lifecycle.start_internal),
		path("<int:pk>/finish-internal/", tournament_lifecycle.finish_internal),
		path("<int:pk>/nenadengi-sync-event-internal/", nenadengi_sync.sync_event_internal),
		path("<int:pk>/nenadengi-sync-results-internal/", nenadengi_sync.sync_results_internal),
		path("nenadengi/webhook/", nenadengi_webhook.NenadengiWebhookView.as_view()),

		path("", include(router.urls)),
	]))
]