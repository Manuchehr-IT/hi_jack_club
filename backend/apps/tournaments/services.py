import logging
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import localtime
from uuid import UUID
from zoneinfo import ZoneInfo

from .models import Tournament, TournamentEventLog, TournamentRegistration
from apps.iiko.services import IikoService

User = get_user_model()

logger = logging.getLogger(__name__)

class TournamentService:
	def __init__(self, iiko_service: IikoService) -> None:
		self.iiko_service = iiko_service
		self.tournament_events = {
			"энтри": "ENTRY", "реэнтри": "RE_ENTRY", "фриэнтри": "FREE_ENTRY", "фриреэнтри": "FREE_RE_ENTRY", "фриэнтри деп": "FREE_ENTRY_DEP", "адон": "ADD_ON",
			"баунтигрин 0.5": "BOUNTY_GREEN", "баунтиблю 0.5": "BOUNTY_BLUE", "баунтиред 0.5": "BOUNTY_RED", "баунтиголд 0.5": "BOUNTY_GOLD",
			"баунтигрин 1": "BOUNTY_GREEN", "баунтиблю 1": "BOUNTY_BLUE", "баунтиред 1": "BOUNTY_RED", "баунтиголд 1": "BOUNTY_GOLD",
			"финишгейм": "ELIMINATION",
		}
		self.entry_all = ["ENTRY", "FREE_ENTRY", "FREE_ENTRY_DEP"]

	def process_olap_report(self, tournament_id: UUID, is_forced: bool = False):
		tournament = Tournament.objects.filter(pk=tournament_id).first()
		if not tournament:
			return

		if not is_forced and (tournament.events.exists() or tournament.olap_report_completed):
			return


		result = self.iiko_service.get_olap_report_by_date(localtime(tournament.started_at).date())

		data = result["data"]

		event_logs = [
			i for i in data
			if i.get("DishName", "").lower() in self.tournament_events
			and i.get("Delivery.CustomerCardNumber") is not None
		]

		cards = {i["Delivery.CustomerCardNumber"] for i in event_logs}
		phones = {f"+7{card}" for card in cards}

		users_map = {u.phone: u for u in User.objects.filter(phone__in=phones)}
		registrations_map = {r.user.phone: r for r in TournamentRegistration.objects.filter(tournament=tournament, user__phone__in=phones).select_related("user")}

		user_events = defaultdict(list)
		for log in event_logs:
			event = self.tournament_events[log["DishName"].lower()]
			user_events[log["Delivery.CustomerCardNumber"]].append(event)

		to_create = []
		moscow_tz = ZoneInfo('Europe/Moscow')

		for event_log in event_logs:
			card = event_log['Delivery.CustomerCardNumber']
			phone = f"+7{card}"
			user = users_map.get(phone)
			reg = registrations_map.get(phone)
			comment = None
			is_valid = False

			if any(entry in user_events[card] for entry in self.entry_all) and "ELIMINATION" in user_events[card]:
				is_valid = True

			if not (user and reg):
				comment = phone
				# is_valid = False

			dish_name = event_log["DishName"].lower()
			event = self.tournament_events[dish_name]
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
					recorded_at=recorded_at,
					comment=comment,
					is_valid=is_valid
				)
			)

		if to_create:
			affected_user_ids = {log.user_id for log in to_create if log.user}
			TournamentEventLog.objects.filter(tournament=tournament).delete()
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
