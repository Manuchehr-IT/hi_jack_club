from uuid import UUID
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Tournament, TournamentRegistration
from apps.iiko.services import IikoService

User = get_user_model()

class TournamentService:
	def __init__(self, iiko_service: IikoService) -> None:
		self.iiko_service = iiko_service

	def process_olap_report(self, tournament_id: UUID):
		tournament = Tournament.objects.filter(pk=tournament_id).first()
		if not tournament:
			return

		tournament_events = {
			"энтри": Decimal("100"), "реэнтри": Decimal("100"), "фриэнтри": Decimal("100"), "фриреэнтри": Decimal("100"), "адон": Decimal("40"),
			"баунтигрин 0.5": Decimal("12.5"), "баунтиблю 0.5": Decimal("25"), "баунтиред 0.5": Decimal("50"), "баунтиголд 0.5": Decimal("25"),
			"баунтигрин 1": Decimal("25"), "баунтиблю 1": Decimal("50"), "баунтиред 1": Decimal("100"), "баунтиголд 1": Decimal("50"),
			"финишгейм": Decimal("0"),
		}

		tournament_points_fond = Decimal("10000")
		tournament_points_fond_distribution = {
			1: Decimal("25"),
			2: Decimal("16"),
			3: Decimal("12"),
			4: Decimal("9"),
			5: Decimal("8"),
			6: Decimal("7"),
			7: Decimal("6"),
			8: Decimal("5.25"),
			9: Decimal("4.25"),
			10: Decimal("2"),
			11: Decimal("1.75"),
			12: Decimal("1.5"),
			13: Decimal("1.25"),
			14: Decimal("1"),
		}
		tournament_points_fond_distribution_top_15 = Decimal("50")

		result = self.iiko_service.get_olap_report_by_date(tournament.created_at.date())
		data = sorted(result["data"], key=lambda x: x["DishServicePrintTime"])

		# phones = {i["Delivery.CustomerPhone"] for i in data}

		events_data = [i for i in data if i.get("DishName", "").lower() in tournament_events and i.get("Delivery.CustomerPhone") is not None]
		finish_game_data = [i for i in events_data if i.get("DishName", "").lower() == "финишгейм"]
		tournament_users = {i["Delivery.CustomerPhone"]: {"knockouts": Decimal("0"), "points": Decimal("0")} for i in events_data}

		for record in events_data:
			event = record["DishName"].lower()
			points = tournament_events.get(event, Decimal("0"))

			tournament_user = tournament_users[record["Delivery.CustomerPhone"]]

			if points > Decimal("0"):
				tournament_user["points"] += points

			if "баунти" in event and "баунтиголд" not in event:
				tournament_user["knockouts"] += Decimal("1")


		top_n = len(tournament_points_fond_distribution)

		for i, record in enumerate(finish_game_data[:top_n], 1):
			percent = tournament_points_fond_distribution[i] / Decimal("100")
			points = tournament_points_fond * percent

			tournament_users[record["Delivery.CustomerPhone"]]["points"] += points

		if len(finish_game_data) >= 15:
			record = finish_game_data[14]
			tournament_users[record["Delivery.CustomerPhone"]]["points"] += tournament_points_fond_distribution_top_15


		phones = list(tournament_users.keys())

		users = User.objects.filter(phone__in=phones)
		users_map = {u.phone: u for u in users}

		registrations = TournamentRegistration.objects.filter(tournament=tournament, user__phone__in=phones).select_related("user")
		registrations_map = {r.user.phone: r for r in registrations}

		to_update = []
		for phone, data in tournament_users.items():
			user = users_map.get(phone)
			if not user:
				continue

			reg = registrations_map.get(phone)
			if not reg:
				continue

			reg.knockouts = data["knockouts"]
			reg.points = data["points"]

			to_update.append(reg)

		TournamentRegistration.objects.bulk_update(to_update, ["knockouts", "points"])
