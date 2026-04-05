import logging
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import localtime
from zoneinfo import ZoneInfo

from .models import Tournament, TournamentEventLog, TournamentRegistration
from apps.iiko.services import IikoService

User = get_user_model()

logger = logging.getLogger(__name__)

class TournamentService:
	def __init__(self, iiko_service: IikoService) -> None:
		self.iiko_service = iiko_service

	def process_olap_report(self, tournament_id: UUID):
		tournament = Tournament.objects.filter(pk=tournament_id).first()
		if not tournament:
			return

		if tournament.events.exists():
			return

		if tournament.olap_report_completed:
			return

		tournament_events = {
			"энтри": "ENTRY", "реэнтри": "RE_ENTRY", "фриэнтри": "FREE_ENTRY", "фриреэнтри": "FREE_RE_ENTRY", "адон": "ADD_ON",
			"баунтигрин 0.5": "BOUNTY_GREEN", "баунтиблю 0.5": "BOUNTY_BLUE", "баунтиред 0.5": "BOUNTY_RED", "баунтиголд 0.5": "BOUNTY_GOLD",
			"баунтигрин 1": "BOUNTY_GREEN", "баунтиблю 1": "BOUNTY_BLUE", "баунтиред 1": "BOUNTY_RED", "баунтиголд 1": "BOUNTY_GOLD",
			"финишгейм": "ELIMINATION",
		}

		result = self.iiko_service.get_olap_report_by_date(localtime(tournament.started_at).date())

		data = sorted(result["data"], key=lambda x: x["DishServicePrintTime"], reverse=True)

		event_logs = [
			i for i in data
			if i.get("DishName", "").lower() in tournament_events
			and i.get("Delivery.CustomerCardNumber") is not None
		]

		phones = {f"+7{i['Delivery.CustomerCardNumber']}" for i in event_logs}

		users_map = {u.phone: u for u in User.objects.filter(phone__in=phones)}
		registrations_map = {r.user.phone: r for r in TournamentRegistration.objects.filter(tournament=tournament, user__phone__in=phones).select_related("user")}

		to_create = []
		moscow_tz = ZoneInfo('Europe/Moscow')

		for event_log in event_logs:
			phone = f"+7{event_log['Delivery.CustomerCardNumber']}"
			user = users_map.get(phone)
			reg = registrations_map.get(phone)

			if not (user and reg):
				continue

			dish_name = event_log["DishName"].lower()
			event = tournament_events[dish_name]
			count = int(event_log["DishAmountInt"])

			multiplier = Decimal("1")
			if "баунти" in dish_name:
				parts = dish_name.split()
				if len(parts) > 1:
					try:
						multiplier = Decimal(parts[-1].replace(",", "."))
					except:
						multiplier = Decimal("1")

			recorded_at = timezone.make_aware(
				datetime.fromisoformat(event_log["DishServicePrintTime"]),
				moscow_tz
			)

			to_create.append(
				TournamentEventLog(
					tournament=tournament,
					user=user,
					event=event,
					count=count,
					multiplier=multiplier,
					recorded_at=recorded_at
				)
			)

		if to_create:
			affected_user_ids = {log.user_id for log in to_create}
			TournamentEventLog.objects.bulk_create(to_create)

			registrations = {
				reg.user_id: reg for reg in TournamentRegistration.objects.filter(tournament=tournament, user_id__in=affected_user_ids)
			}

			for user_id in affected_user_ids:
				registration = registrations.get(user_id)
				if registration:
					registration.recalc_stats()

		tournament.olap_report_completed = True
		tournament.save()

	# def process_olap_report(self, tournament_id: UUID):
	# 	tournament = Tournament.objects.filter(pk=tournament_id).first()
	# 	if not tournament:
	# 		return

	# 	tournament_events = {
	# 		"энтри": Decimal("100"), "реэнтри": Decimal("100"), "фриэнтри": Decimal("100"), "фриреэнтри": Decimal("100"), "адон": Decimal("40"),
	# 		"баунтигрин 0.5": Decimal("12.5"), "баунтиблю 0.5": Decimal("25"), "баунтиред 0.5": Decimal("50"), "баунтиголд 0.5": Decimal("25"),
	# 		"баунтигрин 1": Decimal("25"), "баунтиблю 1": Decimal("50"), "баунтиред 1": Decimal("100"), "баунтиголд 1": Decimal("50"),
	# 		"финишгейм": Decimal("0"),
	# 	}

	# 	tournament_points_fond = Decimal("10000")
	# 	tournament_points_fond_distribution = {
	# 		1: Decimal("25"),
	# 		2: Decimal("16"),
	# 		3: Decimal("12"),
	# 		4: Decimal("9"),
	# 		5: Decimal("8"),
	# 		6: Decimal("7"),
	# 		7: Decimal("6"),
	# 		8: Decimal("5.25"),
	# 		9: Decimal("4.25"),
	# 		10: Decimal("2"),
	# 		11: Decimal("1.75"),
	# 		12: Decimal("1.5"),
	# 		13: Decimal("1.25"),
	# 		14: Decimal("1"),
	# 	}
	# 	tournament_points_fond_distribution_top_15 = Decimal("50")

	# 	result = self.iiko_service.get_olap_report_by_date(tournament.started_at.date())
	# 	data = sorted(result["data"], key=lambda x: x["DishServicePrintTime"], reverse=True)

	# 	# card_numbers = {i["Delivery.CustomerCardNumber"] for i in data}

	# 	events_data = [i for i in data if i.get("DishName", "").lower() in tournament_events and i.get("Delivery.CustomerCardNumber") is not None]
	# 	# logger.info(f"events_data: {events_data}")
	# 	finish_game_data = [i for i in events_data if i.get("DishName", "").lower() == "финишгейм"]
	# 	tournament_users = {i["Delivery.CustomerCardNumber"]: {"knockouts": Decimal("0"), "points": Decimal("0")} for i in events_data}

	# 	for record in events_data:
	# 		count = int(record["DishAmountInt"])
	# 		event = record["DishName"].lower()
	# 		points = tournament_events.get(event, Decimal("0")) * count

	# 		if points > Decimal("0"):
	# 			if "энтри" in event:
	# 				tournament_points_fond += points
	# 			else:
	# 				tournament_users[record["Delivery.CustomerCardNumber"]]["points"] += points

	# 		if "баунти" in event and "баунтиголд" not in event:
	# 			tournament_users[record["Delivery.CustomerCardNumber"]]["knockouts"] += Decimal("1") * count

	# 	top_n = len(tournament_points_fond_distribution)

	# 	logger.info(f"BANK points: {tournament_points_fond}")

	# 	for i, record in enumerate(finish_game_data[:top_n], 1):
	# 		percent = tournament_points_fond_distribution[i] / Decimal("100")
	# 		points = tournament_points_fond * percent

	# 		tournament_users[record["Delivery.CustomerCardNumber"]]["points"] += points

	# 	if len(finish_game_data) >= 15:
	# 		record = finish_game_data[14]
	# 		tournament_users[record["Delivery.CustomerCardNumber"]]["points"] += tournament_points_fond_distribution_top_15

	# 	card_numbers = list(tournament_users.keys())
	# 	phones = [f"+7{card}" for card in card_numbers]
	# 	logger.info(f"count phones: {len(phones)}")

	# 	users = User.objects.filter(phone__in=phones)
	# 	users_map = {u.phone: u for u in users}

	# 	registrations = TournamentRegistration.objects.filter(tournament=tournament, user__phone__in=phones).select_related("user")
	# 	registrations_map = {r.user.phone: r for r in registrations}

	# 	logger.info(f"Users [MAP]: {len(users_map)}")
	# 	logger.info(f"Registrations [MAP]: {len(registrations_map)}")

	# 	to_update = []
	# 	for card_number, data in tournament_users.items():
	# 		phone = f"+7{card_number}"
	# 		user = users_map.get(phone)
	# 		if not user:
	# 			continue

	# 		reg = registrations_map.get(phone)
	# 		if not reg:
	# 			continue

	# 		reg.knockouts = data["knockouts"]
	# 		reg.points = data["points"]

	# 		to_update.append(reg)

	# 	TournamentRegistration.objects.bulk_update(to_update, ["knockouts", "points"])
