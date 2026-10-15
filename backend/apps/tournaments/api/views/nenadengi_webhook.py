import json
import logging

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.nenadengi.security import verify_webhook_signature
from apps.tournaments.models import PartnerRegistration, Tournament, TournamentRegistration
from apps.tournaments.partner_integration import try_auto_link
from apps.tournaments.api.views.tournament_registration import _perform_unregistration

logger = logging.getLogger(__name__)

HEALTH_BODY = {"ok": True, "capabilities": ["registration.created", "registration.cancelled"]}


def _resolve_booking_status(tournament: Tournament) -> str | None:
	"""CONFIRMED / WAITLISTED / None (мест вообще нет) с учётом и своих, и партнёрских броней.

	Связанные (tournament_registration не пусто) партнёрские брони здесь не считаем —
	они уже учтены через свою TournamentRegistration, иначе получится двойной счёт."""
	unlinked_partner_regs = tournament.partner_registrations.filter(tournament_registration__isnull=True)

	registered_count = (
		tournament.registrations.filter(status=TournamentRegistration.StatusType.REGISTERED).count()
		+ unlinked_partner_regs.filter(status=PartnerRegistration.StatusType.CONFIRMED).count()
	)
	if registered_count < tournament.max_participants:
		return PartnerRegistration.StatusType.CONFIRMED

	waitlist_count = (
		tournament.registrations.filter(status=TournamentRegistration.StatusType.WAITLIST).count()
		+ unlinked_partner_regs.filter(status=PartnerRegistration.StatusType.WAITLISTED).count()
	)
	if waitlist_count < tournament.max_waitlist:
		return PartnerRegistration.StatusType.WAITLISTED

	return None


def _handle_registration_created(payload: dict) -> JsonResponse:
	registration_id = payload.get("registration_id")
	event_external_id = payload.get("event_external_id")
	player = payload.get("player") or {}

	if not registration_id or not event_external_id or not player.get("nickname"):
		return JsonResponse({"error": "invalid_payload", "message": "registration_id/event_external_id/player.nickname обязательны"}, status=422)

	existing = PartnerRegistration.objects.filter(partner_registration_id=registration_id).first()
	if existing:
		# Повторная доставка — отдаём тот же ответ, не пересчитываем занятость заново
		if existing.status == PartnerRegistration.StatusType.CONFIRMED:
			return JsonResponse({"accepted": True, "seat": existing.seat})
		return JsonResponse({"accepted": False, "reason": "full", "waitlist": existing.status == PartnerRegistration.StatusType.WAITLISTED})

	try:
		tournament = Tournament.objects.get(pk=event_external_id)
	except (Tournament.DoesNotExist, ValueError):
		return JsonResponse({"error": "event_not_found", "message": f"Турнир '{event_external_id}' не найден"}, status=404)

	partner_player_id = player.get("partner_player_id")
	if not partner_player_id:
		return JsonResponse({"error": "invalid_payload", "message": "player.partner_player_id обязателен"}, status=422)

	with transaction.atomic():
		Tournament.objects.select_for_update().get(pk=tournament.pk)
		status = _resolve_booking_status(tournament)

		if status is None:
			# Полностью занято — фиксируем отклонённую бронь для сверки, но места не выделяем
			PartnerRegistration.objects.create(
				tournament=tournament,
				partner_player_id=partner_player_id,
				partner_registration_id=registration_id,
				nickname=player["nickname"],
				name=player.get("name"),
				tg_username=player.get("tg_username"),
				status=PartnerRegistration.StatusType.REJECTED,
				is_test=bool(payload.get("test")),
			)
			return JsonResponse({"accepted": False, "reason": "full", "waitlist": False})

		partner_reg = PartnerRegistration.objects.create(
			tournament=tournament,
			partner_player_id=partner_player_id,
			partner_registration_id=registration_id,
			nickname=player["nickname"],
			name=player.get("name"),
			tg_username=player.get("tg_username"),
			status=status,
			is_test=bool(payload.get("test")),
		)

	if not partner_reg.is_test:
		try_auto_link(partner_reg)

	if status == PartnerRegistration.StatusType.CONFIRMED:
		return JsonResponse({"accepted": True})
	return JsonResponse({"accepted": False, "reason": "full", "waitlist": True})


def _handle_registration_cancelled(payload: dict) -> JsonResponse:
	registration_id = payload.get("registration_id")
	if not registration_id:
		return JsonResponse({"error": "invalid_payload", "message": "registration_id обязателен"}, status=422)

	partner_reg = PartnerRegistration.objects.filter(partner_registration_id=registration_id).first()
	if not partner_reg:
		# Нечего отменять — отвечаем ок, чтобы не ретраили бесконечно
		return JsonResponse({"accepted": True})

	unregistered = False
	if partner_reg.tournament_registration_id:
		try:
			unregistered, _ = _perform_unregistration(partner_reg.tournament_id, partner_reg.tournament_registration.user)
		except Exception:
			logger.exception(f"Не удалось освободить место при отмене брони nenadengi {registration_id}")

	partner_reg.status = PartnerRegistration.StatusType.CANCELLED
	update_fields = ["status", "updated_at"]
	if unregistered:
		partner_reg.tournament_registration = None
		update_fields.append("tournament_registration")
	partner_reg.save(update_fields=update_fields)

	return JsonResponse({"accepted": True})


@method_decorator(csrf_exempt, name="dispatch")
class NenadengiWebhookView(View):
	def get(self, request):
		return JsonResponse(HEALTH_BODY)

	def post(self, request):
		raw_body = request.body
		timestamp = request.headers.get("X-Nenadengi-Timestamp", "")
		signature = request.headers.get("X-Nenadengi-Signature", "")

		if not verify_webhook_signature(timestamp, raw_body, signature):
			return JsonResponse({"error": "bad_signature"}, status=401)

		try:
			payload = json.loads(raw_body)
		except (ValueError, TypeError):
			return JsonResponse({"error": "invalid_json"}, status=422)

		event_type = payload.get("type")
		if event_type == "registration.created":
			return _handle_registration_created(payload)
		if event_type == "registration.cancelled":
			return _handle_registration_cancelled(payload)

		return JsonResponse({"accepted": False, "reason": "unknown type"}, status=400)
