import logging

import httpx
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.nenadengi.factory import create_nenadengi_client
from apps.tournaments.models import Tournament
from apps.tournaments.partner_integration import build_event_payload, build_results_payload
from apps.tournaments.api.views.tournament_lifecycle import InternalApiPermission

logger = logging.getLogger(__name__)


def _respond_for_nenadengi_error(action: str, pk, err: Exception) -> Response:
	"""Транслирует ошибку вызова nenadengi в код ответа, по которому Celery-таска
	на другой стороне решает, ретраить или нет: 502 — временно (ретраим),
	422 — nenadengi окончательно отклонил, повтор того же payload не поможет."""
	if isinstance(err, httpx.HTTPStatusError):
		status = err.response.status_code
		logger.error(f"Nenadengi [{action}] tournament={pk} status={status}: {err.response.text}")
		if status >= 500 or status == 429:
			return Response({"detail": err.response.text}, status=502)
		return Response({"detail": err.response.text}, status=422)

	logger.error(f"Nenadengi [{action}] tournament={pk}", exc_info=err)
	return Response({"detail": str(err)}, status=502)

@extend_schema(
	tags=["Nenadengi"],
	summary="Отправить афишу турнира в nenadengi",
	description="Только для вызова из Celery worker с правильным X-Internal-Api-Key",
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def sync_event_internal(request, pk):
	"""
	POST /api/tournaments/{id}/nenadengi-sync-event-internal/
	"""
	try:
		tournament = Tournament.objects.get(pk=pk)
	except Tournament.DoesNotExist:
		return Response({"detail": "Турнир не найден"}, status=404)

	client = create_nenadengi_client()
	payload = build_event_payload(tournament)

	try:
		client.upsert_event(payload, idempotency_key=f"event-{tournament.id}-{tournament.updated_at.timestamp()}")
	except Exception as err:
		return _respond_for_nenadengi_error("sync_event", pk, err)

	return Response({"ok": True})

@extend_schema(
	tags=["Nenadengi"],
	summary="Отправить результаты турнира в nenadengi",
	description="Только для вызова из Celery worker с правильным X-Internal-Api-Key",
)
@api_view(["POST"])
@permission_classes([InternalApiPermission])
def sync_results_internal(request, pk):
	"""
	POST /api/tournaments/{id}/nenadengi-sync-results-internal/
	"""
	try:
		tournament = Tournament.objects.get(pk=pk)
	except Tournament.DoesNotExist:
		return Response({"detail": "Турнир не найден"}, status=404)

	client = create_nenadengi_client()
	payload = build_results_payload(tournament)

	try:
		client.post_results(str(tournament.id), payload, idempotency_key=f"results-{tournament.id}-{tournament.updated_at.timestamp()}")
	except Exception as err:
		return _respond_for_nenadengi_error("sync_results", pk, err)

	return Response({"ok": True})
