"""Хелперы интеграции с nenadengi: линковка гостей партнёра с нашими User
и сборка payload'ов для /events и /events/{id}/results."""

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import PartnerRegistration, Tournament, TournamentRegistration

User = get_user_model()

_EVENT_STATUS_MAP = {
	Tournament.StatusType.IN_QUEUE: "scheduled",
	Tournament.StatusType.ACTIVE: "running",
	Tournament.StatusType.INACTIVE: "finalized",
}

_PARTNER_TO_OUR_STATUS = {
	PartnerRegistration.StatusType.CONFIRMED: TournamentRegistration.StatusType.REGISTERED,
	PartnerRegistration.StatusType.WAITLISTED: TournamentRegistration.StatusType.WAITLIST,
	# REJECTED/CANCELLED сюда попадают только через ручную линковку в админке
	# (автоматическая линковка на эти статусы не вызывается вовсе) — трактуем
	# как осознанное решение админа засчитать участие, поэтому тоже REGISTERED.
	PartnerRegistration.StatusType.REJECTED: TournamentRegistration.StatusType.REGISTERED,
	PartnerRegistration.StatusType.CANCELLED: TournamentRegistration.StatusType.REGISTERED,
}


def link_partner_registration(partner_reg: PartnerRegistration, user) -> TournamentRegistration:
	"""Связывает бронь партнёра с нашим User и заводит (если ещё нет) обычную
	TournamentRegistration — дальше вся судьба очков идёт через неё."""
	with transaction.atomic():
		if not user.nenadengi_id:
			user.nenadengi_id = partner_reg.partner_player_id
			user.save(update_fields=["nenadengi_id"])

		tournament_registration, _ = TournamentRegistration.objects.get_or_create(
			tournament=partner_reg.tournament,
			user=user,
			defaults={
				"status": _PARTNER_TO_OUR_STATUS.get(partner_reg.status, TournamentRegistration.StatusType.REGISTERED),
				"source": TournamentRegistration.SourceType.NENADENGI,
			}
		)

		partner_reg.user = user
		partner_reg.tournament_registration = tournament_registration
		partner_reg.save(update_fields=["user", "tournament_registration", "updated_at"])

	return tournament_registration


def unlink_partner_registration(partner_reg: PartnerRegistration) -> None:
	"""Откатывает линковку (например, если по ошибке выбрали не того пользователя).
	Удаляет заведённую TournamentRegistration, только если по ней ещё нет
	реального результата (attended=False) — иначе её могли заполнить не просто так,
	трогать не будем, просто отвязываем ссылку. Также снимает nenadengi_id с
	пользователя, если он до сих пор указывает именно на эту бронь."""
	with transaction.atomic():
		tournament_registration = partner_reg.tournament_registration
		user = partner_reg.user

		partner_reg.user = None
		partner_reg.tournament_registration = None
		partner_reg.save(update_fields=["user", "tournament_registration", "updated_at"])

		if tournament_registration and not tournament_registration.attended:
			tournament_registration.delete()

		if user and user.nenadengi_id == partner_reg.partner_player_id:
			user.nenadengi_id = None
			user.save(update_fields=["nenadengi_id"])


def try_auto_link(partner_reg: PartnerRegistration) -> TournamentRegistration | None:
	"""Если гость уже когда-то был связан с нашим User по nenadengi_id — линкуем сразу."""
	user = User.objects.filter(nenadengi_id=partner_reg.partner_player_id).first()
	if not user:
		return None
	return link_partner_registration(partner_reg, user)


def build_event_payload(tournament: Tournament) -> dict:
	return {
		"external_id": str(tournament.id),
		"starts_at": tournament.started_at.isoformat(),
		"title": tournament.title,
		"game_type": "tournament",
		"buy_in": tournament.buy_in,
		"currency": tournament.currency,
		"capacity_seats": tournament.max_participants,
		"registerable": tournament.registerable and tournament.status == Tournament.StatusType.IN_QUEUE,
		"status": _EVENT_STATUS_MAP.get(tournament.status, "scheduled"),
	}


def build_cancelled_event_payload(tournament: Tournament) -> dict:
	payload = build_event_payload(tournament)
	payload["status"] = "cancelled"
	return payload


def build_results_payload(tournament: Tournament) -> dict:
	"""Полный ростер турнира — свои TournamentRegistration + ещё не связанные
	брони партнёра (у которых результат по-прежнему лежит на самой брони)."""
	players = []

	registrations = (
		tournament.registrations
		.filter(attended=True)
		.select_related("user", "partner_registration")
	)
	for reg in registrations:
		entry = {
			"nickname": reg.user.nickname,
			"player_ref": str(reg.user.id),
		}
		if reg.place:
			entry["place"] = reg.place
		if reg.payout:
			entry["payout"] = reg.payout

		partner_reg = getattr(reg, "partner_registration", None)
		nenadengi_id = partner_reg.partner_player_id if partner_reg else reg.user.nenadengi_id
		if nenadengi_id:
			entry["partner_player_id"] = str(nenadengi_id)

		players.append(entry)

	unlinked_partner_regs = tournament.partner_registrations.filter(
		tournament_registration__isnull=True,
		is_test=False,
		attended=True,
	)
	for partner_reg in unlinked_partner_regs:
		entry = {
			"nickname": partner_reg.nickname,
			"partner_player_id": str(partner_reg.partner_player_id),
		}
		if partner_reg.place:
			entry["place"] = partner_reg.place
		if partner_reg.payout:
			entry["payout"] = partner_reg.payout
		players.append(entry)

	return {
		"status": "finalized",
		"field_size": len(players),
		"players": players,
	}
